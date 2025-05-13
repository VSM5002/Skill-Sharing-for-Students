from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
from dotenv import load_dotenv
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime
from flask import jsonify, redirect

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

# Database connection
db = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', 'password'),
    database=os.getenv('DB_NAME', 'skill_sharing')
)
cursor = db.cursor()

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')  # e.g., smtp.outlook.com
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))  # e.g., 587
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')  # Your Outlook email
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')  # Your Outlook email password
mail = Mail(app)

# Token Serializer
serializer = URLSafeTimedSerializer(app.secret_key)

# Allowed email domain for registration
ALLOWED_EMAIL_DOMAIN = os.getenv('ALLOWED_EMAIL_DOMAIN', 'example.com')

# In-memory storage for profile requests (replace with database in production)
profile_requests = {}

# Replace this in-memory enrolled_courses with a persistent table in your database.
# Add this table to your database (run this SQL once):
# CREATE TABLE enrolled_courses (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     user_id INT,
#     skill_id INT,
#     course_id INT,
#     UNIQUE KEY unique_enroll (user_id, skill_id, course_id)
# );

# Table for requests (if not already created, add to your SQL):
# CREATE TABLE IF NOT EXISTS requests (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     sender_id INT NOT NULL,
#     receiver_id INT NOT NULL,
#     status VARCHAR(20) DEFAULT 'pending',
#     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
#     FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
#     FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
# );

# Routes
@app.route('/')
def main_page():
    completion_percentage = 50  # Example value, replace with actual logic
    return render_template('home.html', completion_percentage=completion_percentage)  # Ensure 'home.html' exists

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT id, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user or not check_password_hash(user[1], password):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('login'))
        session['user_id'] = user[0]
        flash('Login successful!', 'success')
        return redirect(url_for('homepage'))  # Redirect to the homepage after login
    return render_template('login.html')  # Ensure 'login.html' exists

@app.route('/homepage')
def homepage():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Fetch skills from the database (remove image_url)
    cursor.execute("SELECT name, description FROM skills LIMIT 30")
    skills = cursor.fetchall()
    return render_template('homepage.html', skills=skills)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        # Validate email domain
        if not email.endswith(f"@{ALLOWED_EMAIL_DOMAIN}"):
            flash('Only students with a valid college email can register.', 'error')
            return redirect(url_for('register'))

        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash('Email already exists.', 'error')
            return redirect(url_for('register'))
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )
        db.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')  # Ensure 'register.html' exists

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    logged_in_user = session['user_id']

    # Fetch user details
    cursor.execute("SELECT name, email FROM users WHERE id = %s", (logged_in_user,))
    user_details = cursor.fetchone()

    # Fetch pending profile requests for the user
    user_requests = [req for req in profile_requests if req['receiver'] == logged_in_user and req['status'] == "pending"]

    return render_template('dashboard.html', user_details=user_details, user_requests=user_requests)  # Ensure 'dashboard.html' exists

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    if request.method == 'POST':
        name = request.form.get('name')
        skills = request.form.get('skills')
        # Add more fields as needed
        cursor.execute("UPDATE users SET name=%s, skills=%s WHERE id=%s", (name, skills, user_id))
        db.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    cursor.execute("SELECT name, email, bio, skills, contact, education, experience FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    user_email = user[1]
    cursor.execute("SELECT skill_id FROM enrolled_skills WHERE user_id = %s", (user_id,))
    enrolled = cursor.fetchall()
    enrolled_links = []
    for (skill_id,) in enrolled:
        cursor.execute("SELECT name FROM skills WHERE id = %s", (skill_id,))
        skill_name = cursor.fetchone()
        if skill_name:
            enrolled_links.append({
                "skill_id": skill_id,
                "skill_name": skill_name[0]
            })
    return render_template('profile.html', user=user, user_email=user_email, enrolled_links=enrolled_links)

@app.route('/add_skill', methods=['GET', 'POST'])
def add_skill():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        skill_name = request.form['skill_name']
        description = request.form['description']
        prerequisites = request.form['prerequisites']
        user_id = session['user_id']
        cursor.execute(
            "INSERT INTO skills (name, description, prerequisites, user_id) VALUES (%s, %s, %s, %s)",
            (skill_name, description, prerequisites, user_id)
        )
        db.commit()
        flash('Skill added successfully!', 'success')
        return redirect(url_for('add_skill'))  # Redirect to add_skill page to show the message
    return render_template('add_skill.html')  # Ensure 'add_skill.html' exists

@app.route('/search', methods=['GET'])
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    query = request.args.get('query', '')
    results = []
    if query:
        cursor.execute("""
            SELECT id, name, email, skills
            FROM users
            WHERE name LIKE %s OR skills LIKE %s
        """, (f"%{query}%", f"%{query}%"))
        user_results = cursor.fetchall()
        cursor.execute("""
            SELECT id, name, description
            FROM skills
            WHERE name LIKE %s OR description LIKE %s
        """, (f"%{query}%", f"%{query}%"))
        skill_results = cursor.fetchall()
        results = {
            "users": user_results,
            "skills": skill_results
        }
    return render_template('search.html', results=results, query=query)

@app.route('/skill/<int:skill_id>', methods=['GET', 'POST'])
def skill_details(skill_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    # Fetch skill details (name, description, prerequisites, user_id)
    cursor.execute("""
        SELECT name, description, prerequisites, user_id
        FROM skills
        WHERE id = %s
    """, (skill_id,))
    skill = cursor.fetchone()

    # Get the image filename based on homepage convention
    image_map = {
        1: "python.jpeg",
        2: "web_development.png",
        3: "data_science.jpeg",
        4: "graphic_design.jpeg",
        5: "digital_marketing.jpeg",
        6: "photography.jpeg",
        7: "video_editing.jpeg",
        8: "public_speaking.jpeg",
        9: "cooking.jpeg",
        10: "yoga.jpeg",
        11: "machine_learning.jpeg",
        12: "blockchain.jpeg",
        13: "cyberscurity.jpeg",
        14: "cloud_computing.jpeg",
        15: "devops.png",
        16: "artificial_intelligence.jpeg",
        17: "mobile_app.jpeg",
        18: "game_development.jpeg",
        19: "ethical_hacking.jpeg",
        20: "robotics.jpeg",
        21: "3d_modeling.jpeg",
        22: "UI_UX.png",
        23: "big_data.jpeg",
        24: "Agumented_reality.jpeg",
        25: "virtual_reality.jpeg",
        26: "e_commerce.jpeg",
        27: "content_writing.jpeg",
        28: "animation.jpeg",
        29: "music_production.jpeg",
        30: "fitness_training.jpeg"
    }
    image_url = "/static/images/" + image_map.get(skill_id, "default.jpeg")

    # Fetch teachers for the skill (users who have this skill)
    cursor.execute("""
        SELECT name
        FROM users
        WHERE id = %s
    """, (skill[3],))
    teachers = cursor.fetchall()

    # Dummy courses and chapters for demonstration, all progress 0%
    courses = [
        {
            "id": 1,
            "title": f"Course 1 for {skill[0]}",
            "progress": 0,
            "chapters": ["Chapter 1", "Chapter 2", "Chapter 3"]
        },
        {
            "id": 2,
            "title": f"Course 2 for {skill[0]}",
            "progress": 0,
            "chapters": ["Chapter 1", "Chapter 2"]
        },
        {
            "id": 3,
            "title": f"Course 3 for {skill[0]}",
            "progress": 0,
            "chapters": ["Chapter 1", "Chapter 2", "Chapter 3", "Chapter 4"]
        },
        {
            "id": 4,
            "title": f"Course 4 for {skill[0]}",
            "progress": 0,
            "chapters": ["Chapter 1"]
        }
    ]

    # Handle enroll POST (enroll for the skill, not for a course)
    if request.method == 'POST':
        cursor.execute(
            "INSERT IGNORE INTO enrolled_skills (user_id, skill_id) VALUES (%s, %s)",
            (user_id, skill_id)
        )
        db.commit()
        flash('Enrolled in skill successfully!', 'success')
        return redirect(url_for('skill_details', skill_id=skill_id))

    # Check if user is enrolled for this skill
    cursor.execute(
        "SELECT 1 FROM enrolled_skills WHERE user_id = %s AND skill_id = %s",
        (user_id, skill_id)
    )
    is_enrolled = cursor.fetchone() is not None

    return render_template(
        'skill_details.html',
        skill=skill,
        teachers=teachers,
        image_url=image_url,
        courses=courses,
        is_enrolled=is_enrolled
    )

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main_page'))  # Redirects to 'home.html'

@app.route('/send_verification_email', methods=['POST'])
def send_verification_email():
    email = request.form.get('email')
    token = serializer.dumps(email, salt='email-verification')
    verification_url = url_for('verify_email', token=token, _external=True)

    # Send email
    msg = Message('Verify Your Email', sender=app.config['MAIL_USERNAME'], recipients=[email])
    msg.body = f'Click the link to verify your email: {verification_url}'
    mail.send(msg)

    flash('Verification email sent. Please check your inbox.', 'success')
    return redirect(url_for('homepage'))

@app.route('/verify_email', methods=['POST'])
def verify_email():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Fetch the user's email from the database
        cursor.execute("SELECT email FROM users WHERE id = %s", (session['user_id'],))
        user = cursor.fetchone()
        if not user:
            flash("User not found.", "error")
            return redirect(url_for('profile'))

        email = user[0]
        token = serializer.dumps(email, salt='email-verification')
        verification_url = url_for('verify_email_token', token=token, _external=True)

        # Send verification email
        msg = Message('Verify Your Email', sender=app.config['MAIL_USERNAME'], recipients=[email])
        msg.body = f'Click the link to verify your email: {verification_url}'
        mail.send(msg)

        flash('Verification email sent. Please check your inbox.', 'success')
    except Exception as e:
        flash(f"An error occurred while sending the email: {str(e)}", "error")
    return redirect(url_for('profile'))

@app.route('/verify_email/<token>', methods=['GET'])
def verify_email_token(token):
    try:
        email = serializer.loads(token, salt='email-verification', max_age=3600)  # Token valid for 1 hour
        cursor.execute("UPDATE users SET email_verified = 1 WHERE email = %s", (email,))
        db.commit()
        flash('Email verified successfully!', 'success')
    except Exception as e:
        flash('The verification link is invalid or has expired.', 'error')
    return redirect(url_for('profile'))

@app.route('/test_email')
def test_email():
    try:
        msg = Message(
            subject="Test Email",
            sender=app.config['MAIL_USERNAME'],
            recipients=["recipient@example.com"],  # Replace with a valid recipient email
            body="This is a test email sent from Flask using Outlook."
        )
        mail.send(msg)
        return "Test email sent successfully!"
    except Exception as e:
        return f"Failed to send email: {str(e)}"

@app.route('/send_request', methods=['POST'])
def send_request():
    if 'user_id' not in session:
        flash('You must be logged in to send a request.', 'error')
        return redirect(url_for('search'))
    sender_id = session['user_id']
    receiver_id = request.form.get('receiver_id')
    if not receiver_id:
        flash('Receiver ID required.', 'error')
        return redirect(url_for('search'))
    cursor.execute("SELECT id FROM requests WHERE sender_id=%s AND receiver_id=%s AND status='pending'", (sender_id, receiver_id))
    if cursor.fetchone():
        flash('Request already sent.', 'error')
        return redirect(url_for('search'))
    cursor.execute("INSERT INTO requests (sender_id, receiver_id) VALUES (%s, %s)", (sender_id, receiver_id))
    db.commit()
    flash('Request sent successfully!', 'success')
    return redirect(url_for('search'))

@app.route('/requests')
def view_requests():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    cursor.execute("""
        SELECT r.id, u.name, u.email, r.status, r.timestamp
        FROM requests r
        JOIN users u ON r.sender_id = u.id
        WHERE r.receiver_id = %s
        ORDER BY r.timestamp DESC
    """, (user_id,))
    requests_list = cursor.fetchall()
    return render_template('requests.html', requests=requests_list)

@app.route('/accept_request/<int:request_id>', methods=['POST'])
def accept_request(request_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Only the receiver can accept the request
    cursor.execute("SELECT receiver_id FROM requests WHERE id=%s", (request_id,))
    row = cursor.fetchone()
    if not row or row[0] != session['user_id']:
        flash('Unauthorized action.', 'error')
        return redirect(url_for('view_requests'))
    cursor.execute("UPDATE requests SET status='accepted' WHERE id=%s", (request_id,))
    db.commit()
    flash('Request accepted.', 'success')
    return redirect(url_for('view_requests'))

@app.route('/certificates')
def certificates():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    cursor.execute("SELECT name, issued_by, issued_on FROM certificates WHERE user_id = %s", (session['user_id'],))
    certificates = [
        {'name': row[0], 'issued_by': row[1], 'issued_on': row[2]}
        for row in cursor.fetchall()
    ]
    return render_template('certificates.html', certificates=certificates)

@app.route('/populate_skills')
def populate_skills():
    skills = [
        ("Python Programming", "Learn the basics of Python programming.", "https://via.placeholder.com/200x150?text=Python"),
        ("Web Development", "Build modern websites using HTML, CSS, and JavaScript.", "https://via.placeholder.com/200x150?text=Web+Development"),
        ("Data Science", "Analyze data and build machine learning models.", "https://via.placeholder.com/200x150?text=Data+Science"),
        ("Graphic Design", "Create stunning visuals using design tools.", "https://via.placeholder.com/200x150?text=Graphic+Design"),
        ("Digital Marketing", "Learn SEO, social media marketing, and more.", "https://via.placeholder.com/200x150?text=Digital+Marketing"),
        ("Photography", "Master the art of capturing stunning photos.", "https://via.placeholder.com/200x150?text=Photography"),
        ("Video Editing", "Learn to edit videos like a pro.", "https://via.placeholder.com/200x150?text=Video+Editing"),
        ("Public Speaking", "Enhance your communication and presentation skills.", "https://via.placeholder.com/200x150?text=Public+Speaking"),
        ("Cooking", "Learn to cook delicious meals.", "https://via.placeholder.com/200x150?text=Cooking"),
        ("Yoga", "Improve your flexibility and mental health.", "https://via.placeholder.com/200x150?text=Yoga"),
        ("Machine Learning", "Learn to build predictive models using data.", "https://via.placeholder.com/200x150?text=Machine+Learning"),
        ("Blockchain", "Understand the fundamentals of blockchain technology.", "https://via.placeholder.com/200x150?text=Blockchain"),
        ("Cybersecurity", "Protect systems and networks from cyber threats.", "https://via.placeholder.com/200x150?text=Cybersecurity"),
        ("Cloud Computing", "Learn to deploy and manage applications in the cloud.", "https://via.placeholder.com/200x150?text=Cloud+Computing"),
        ("DevOps", "Master CI/CD pipelines and automation tools.", "https://via.placeholder.com/200x150?text=DevOps"),
        ("Artificial Intelligence", "Explore AI concepts and applications.", "https://via.placeholder.com/200x150?text=Artificial+Intelligence"),
        ("Mobile App Development", "Create mobile apps for Android and iOS.", "https://via.placeholder.com/200x150?text=Mobile+App+Development"),
        ("Game Development", "Design and develop engaging video games.", "https://via.placeholder.com/200x150?text=Game+Development"),
        ("Ethical Hacking", "Learn to identify and fix security vulnerabilities.", "https://via.placeholder.com/200x150?text=Ethical+Hacking"),
        ("Robotics", "Build and program robots for various tasks.", "https://via.placeholder.com/200x150?text=Robotics"),
        ("3D Modeling", "Create 3D models for games and animations.", "https://via.placeholder.com/200x150?text=3D+Modeling"),
        ("UI/UX Design", "Design user-friendly interfaces and experiences.", "https://via.placeholder.com/200x150?text=UI%2FUX+Design"),
        ("Big Data", "Analyze and process large datasets efficiently.", "https://via.placeholder.com/200x150?text=Big+Data"),
        ("Augmented Reality", "Create immersive AR experiences.", "https://via.placeholder.com/200x150?text=Augmented+Reality"),
        ("Virtual Reality", "Develop VR applications and simulations.", "https://via.placeholder.com/200x150?text=Virtual+Reality"),
        ("E-commerce", "Build and manage online stores.", "https://via.placeholder.com/200x150?text=E-commerce"),
        ("Content Writing", "Write engaging and impactful content.", "https://via.placeholder.com/200x150?text=Content+Writing"),
        ("Animation", "Create stunning animations for videos and games.", "https://via.placeholder.com/200x150?text=Animation"),
        ("Music Production", "Compose and produce music tracks.", "https://via.placeholder.com/200x150?text=Music+Production"),
        ("Fitness Training", "Learn to stay fit and healthy.", "https://via.placeholder.com/200x150?text=Fitness+Training")
    ]

    try:
        cursor.executemany(
            "INSERT INTO skills (name, description, image_url) VALUES (%s, %s, %s)",
            skills
        )
        db.commit()
        return "Skills populated successfully!"
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)  # Ensure debug mode is enabled

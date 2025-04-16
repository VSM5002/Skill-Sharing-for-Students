from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import mysql.connector
import secrets
import os
from dotenv import load_dotenv

# Load environment variables from .env file
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

# Flask-Mail configuration
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
mail = Mail(app)

# Routes
@app.route('/')
def main_page():
    return render_template('main.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        # Check if the email already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash('Email already exists. Please use a different email.', 'error')
            return redirect(url_for('register'))

        verification_token = secrets.token_urlsafe(16)  # Generate a unique token
        cursor.execute(
            "INSERT INTO users (name, email, password, verification_token, is_verified) VALUES (%s, %s, %s, %s, %s)",
            (name, email, password, verification_token, False)
        )
        db.commit()

        # Send verification email
        verification_link = url_for('verify_email', token=verification_token, _external=True)
        msg = Message('Verify Your Email', sender='your_email@gmail.com', recipients=[email])
        msg.body = f"Hi {name},\n\nPlease verify your email by clicking the link below:\n{verification_link}\n\nThank you!"
        mail.send(msg)

        flash('A verification email has been sent to your email address. Please verify your email to log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/verify_email/<token>')
def verify_email(token):
    # Check if the token exists in the database
    cursor.execute("SELECT id FROM users WHERE verification_token = %s", (token,))
    user = cursor.fetchone()
    if user:
        # Update the user's email as verified
        cursor.execute("UPDATE users SET is_verified = 1, verification_token = NULL WHERE id = %s", (user[0],))
        db.commit()
        flash('Your email has been verified. You can now log in.', 'success')
        return redirect(url_for('login'))
    else:
        flash('Invalid or expired verification link.', 'error')
        return redirect(url_for('main_page'))  # Redirect to main page instead of profile

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT id, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            flash('Email is not registered. Please register first.', 'error')
            return redirect(url_for('login'))
        
        if not check_password_hash(user[1], password):
            flash('Incorrect password. Please try again.', 'error')
            return redirect(url_for('login'))
        
        session['user_id'] = user[0]
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            flash('Email is not registered. Please register first.', 'error')
            return redirect(url_for('forgot_password'))
        # Generate a reset token and send an email
        reset_token = secrets.token_urlsafe(16)
        cursor.execute("UPDATE users SET verification_token = %s WHERE id = %s", (reset_token, user[0]))
        db.commit()
        reset_link = url_for('reset_password', token=reset_token, _external=True)
        msg = Message('Reset Your Password', sender='your_email@gmail.com', recipients=[email])
        msg.body = f"Hi,\n\nClick the link below to reset your password:\n{reset_link}\n\nThank you!"
        mail.send(msg)
        flash('A password reset link has been sent to your email.', 'info')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if request.method == 'POST':
        new_password = generate_password_hash(request.form['password'])
        cursor.execute("UPDATE users SET password = %s, verification_token = NULL WHERE verification_token = %s", (new_password, token))
        db.commit()
        flash('Your password has been reset. You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main_page'))  # Redirect to main page after logout

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    search_results = None
    if request.method == 'POST' and 'search_query' in request.form:
        # Handle search functionality
        query = request.form['search_query']
        cursor.execute("""
            SELECT users.id, users.name, GROUP_CONCAT(skills.name SEPARATOR ', ') AS skills
            FROM users
            LEFT JOIN user_skills ON users.id = user_skills.user_id
            LEFT JOIN skills ON user_skills.skill_id = skills.id
            WHERE users.name LIKE %s OR skills.name LIKE %s
            GROUP BY users.id
        """, (f"%{query}%", f"%{query}%"))
        search_results = cursor.fetchall()
    
    cursor.execute("SELECT name, email, is_verified FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    recommendations = ["C Programming", "C++ Programming", "Python Programming", "Java Programming", "JavaScript Programming", "AI & Machine Learning", "Data Science"]
    return render_template('dashboard.html', user=user, recommendations=recommendations, search_results=search_results)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        if 'verify_email' in request.form:
            # Handle email verification
            cursor.execute("SELECT email, is_verified FROM users WHERE id = %s", (session['user_id'],))
            user = cursor.fetchone()
            if user and not user[1]:  # If email is not verified
                verification_token = secrets.token_urlsafe(16)
                cursor.execute("UPDATE users SET verification_token = %s WHERE id = %s", (verification_token, session['user_id']))
                db.commit()
                verification_link = url_for('verify_email', token=verification_token, _external=True)
                msg = Message('Verify Your Email', sender=os.getenv('MAIL_USERNAME'), recipients=[user[0]])
                msg.body = f"Hi,\n\nPlease verify your email by clicking the link below:\n{verification_link}\n\nThank you!"
                try:
                    mail.send(msg)
                    flash('Verification email sent. Please check your inbox.', 'success')
                except Exception as e:
                    flash(f'Failed to send verification email: {e}', 'error')
            else:
                flash('Your email is already verified.', 'info')
        else:
            # Handle profile updates
            bio = request.form['bio']
            skills = request.form['skills']
            contact = request.form['contact']
            education = request.form['education']
            experience = request.form['experience']
            cursor.execute(
                "UPDATE users SET bio = %s, skills = %s, contact = %s, education = %s, experience = %s WHERE id = %s",
                (bio, skills, contact, education, experience, session['user_id'])
            )
            db.commit()
            flash('Profile updated successfully.', 'success')
    cursor.execute(
        "SELECT name, email, bio, skills, contact, education, experience, is_verified FROM users WHERE id = %s",
        (session['user_id'],)
    )
    user = cursor.fetchone()
    return render_template('profile.html', user=user)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    cursor.execute("""
        SELECT users.name, GROUP_CONCAT(skills.name) AS skills
        FROM users
        LEFT JOIN user_skills ON users.id = user_skills.user_id
        LEFT JOIN skills ON user_skills.skill_id = skills.id
        WHERE skills.name LIKE %s OR users.name LIKE %s
        GROUP BY users.id
    """, (f"%{query}%", f"%{query}%"))
    results = cursor.fetchall()
    return render_template('search.html', results=results)

@app.route('/send_request/<int:receiver_id>', methods=['POST'])
def send_request(receiver_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Insert the request into the requests table
    cursor.execute("INSERT INTO requests (sender_id, receiver_id) VALUES (%s, %s)", (session['user_id'], receiver_id))
    db.commit()
    flash('Request sent successfully!', 'success')
    return redirect(url_for('search'))

@app.route('/requests')
def view_requests():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Fetch all requests sent to the logged-in user
    cursor.execute("""
        SELECT users.name, users.email, requests.id
        FROM requests
        JOIN users ON requests.sender_id = users.id
        WHERE requests.receiver_id = %s
    """, (session['user_id'],))
    requests = cursor.fetchall()
    return render_template('requests.html', requests=requests)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        if 'delete_account' in request.form:
            # Delete the user's account
            cursor.execute("DELETE FROM users WHERE id = %s", (session['user_id'],))
            db.commit()
            session.pop('user_id', None)
            flash('Your account has been deleted successfully.')
            return redirect(url_for('main_page'))
    return render_template('settings.html')

@app.route('/test_email')
def test_email():
    try:
        msg = Message('Test Email', sender='your_email@gmail.com', recipients=['recipient_email@gmail.com'])
        msg.body = 'This is a test email from Flask-Mail.'
        mail.send(msg)
        return 'Test email sent successfully!'
    except Exception as e:
        return f'Failed to send email: {e}'

@app.route('/skill/<int:skill_id>')
def skill_details(skill_id):
    # Fetch skill details from the database
    cursor.execute("SELECT id, name, description, prerequisites FROM skills WHERE id = %s", (skill_id,))
    skill = cursor.fetchone()
    if not skill:
        flash('Skill not found.', 'error')
        return redirect(url_for('dashboard'))
    return render_template('skill_details.html', skill=skill)

@app.route('/add_skill', methods=['GET', 'POST'])
def add_skill():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        skill_name = request.form['skill_name']
        description = request.form['description']
        prerequisites = request.form['prerequisites']
        cursor.execute(
            "INSERT INTO skills (name, description, prerequisites) VALUES (%s, %s, %s)",
            (skill_name, description, prerequisites)
        )
        db.commit()
        flash('Skill added successfully!', 'success')  # Flash the success message
        return redirect(url_for('dashboard'))  # Redirect to the dashboard
    return render_template('add_skill.html')

@app.route('/add_user_skills', methods=['GET', 'POST'])
def add_user_skills():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        skill_ids = request.form.getlist('skills')  # List of selected skill IDs
        cursor.execute("DELETE FROM user_skills WHERE user_id = %s", (session['user_id'],))  # Clear existing skills
        for skill_id in skill_ids:
            cursor.execute("INSERT INTO user_skills (user_id, skill_id) VALUES (%s, %s)", (session['user_id'], skill_id))
        db.commit()
        flash('Skills updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    cursor.execute("SELECT id, name FROM skills")  # Fetch all available skills
    skills = cursor.fetchall()
    cursor.execute("SELECT skill_id FROM user_skills WHERE user_id = %s", (session['user_id'],))  # Fetch user's skills
    user_skills = [row[0] for row in cursor.fetchall()]
    return render_template('add_user_skills.html', skills=skills, user_skills=user_skills)

@app.route('/search_users', methods=['GET', 'POST'])
def search_users():
    query = request.form.get('query', '') if request.method == 'POST' else request.args.get('query', '')
    skill_id = request.form.get('skill_id') if request.method == 'POST' else request.args.get('skill_id')
    results = []

    if skill_id:
        # Search by skill ID
        cursor.execute("""
            SELECT users.id, users.name, users.email, GROUP_CONCAT(skills.name SEPARATOR ', ') AS skills
            FROM users
            JOIN user_skills ON users.id = user_skills.user_id
            JOIN skills ON user_skills.skill_id = skills.id
            WHERE skills.id = %s
            GROUP BY users.id
        """, (skill_id,))
        results = cursor.fetchall()
    elif query:
        # Search by name or skill name
        cursor.execute("""
            SELECT users.id, users.name, users.email, GROUP_CONCAT(skills.name SEPARATOR ', ') AS skills
            FROM users
            LEFT JOIN user_skills ON users.id = user_skills.user_id
            LEFT JOIN skills ON user_skills.skill_id = skills.id
            WHERE users.name LIKE %s OR skills.name LIKE %s
            GROUP BY users.id
        """, (f"%{query}%", f"%{query}%"))
        results = cursor.fetchall()

    cursor.execute("SELECT id, name FROM skills")  # Fetch all skills for dropdown
    skills = cursor.fetchall()
    return render_template('search_users.html', results=results, skills=skills, query=query, skill_id=skill_id)

if __name__ == '__main__':
    app.run(debug=True)

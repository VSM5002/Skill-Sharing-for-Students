from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
from dotenv import load_dotenv

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
    # Fetch skills from the database
    cursor.execute("SELECT name, description, image_url FROM skills LIMIT 30")
    skills = cursor.fetchall()
    return render_template('homepage.html', skills=skills)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
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
    return render_template('dashboard.html')  # Ensure 'dashboard.html' exists

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    cursor.execute("SELECT name, email FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    return render_template('profile.html', user=user)  # Ensure 'profile.html' exists

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
        flash('Skill added successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('add_skill.html')  # Ensure 'add_skill.html' exists

@app.route('/search')
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    query = request.args.get('query', '')
    cursor.execute("""
        SELECT users.name, GROUP_CONCAT(skills.name SEPARATOR ', ') AS skills
        FROM users
        LEFT JOIN user_skills ON users.id = user_skills.user_id
        LEFT JOIN skills ON user_skills.skill_id = skills.id
        WHERE users.name LIKE %s OR skills.name LIKE %s
        GROUP BY users.id
    """, (f"%{query}%", f"%{query}%"))
    results = cursor.fetchall()
    return render_template('search.html', results=results)  # Ensure 'search.html' exists

@app.route('/skill/<int:skill_id>')
def skill_details(skill_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Fetch skill details (name, description)
    cursor.execute("""
        SELECT name, description 
        FROM skills 
        WHERE id = %s
    """, (skill_id,))
    skill = cursor.fetchone()

    # Fetch teachers for the skill
    cursor.execute("""
        SELECT users.name 
        FROM users
        JOIN user_skills ON users.id = user_skills.user_id
        WHERE user_skills.skill_id = %s
    """, (skill_id,))
    teachers = cursor.fetchall()

    # Check if skill exists
    if not skill:
        flash("Skill not found.", "error")
        return redirect(url_for('homepage'))

    return render_template('skill_details.html', skill=skill, teachers=teachers)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('main_page'))  # Redirects to 'home.html'

if __name__ == '__main__':
    app.run(debug=True)

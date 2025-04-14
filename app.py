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
        cursor.execute("UPDATE users SET is_verified = 1, verification_token = NULL WHERE verification_token = %s", (token,))
        db.commit()
        flash('Your email has been verified. You can now log in.', 'success')
        return redirect(url_for('login'))
    else:
        flash('Invalid or expired verification link.', 'error')
        return redirect(url_for('profile'))

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
    
    if request.method == 'POST' and 'verify_email' in request.form:
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
    
    cursor.execute("SELECT name, email, is_verified FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    recommendations = ["C Programming", "C++ Programming", "Python Programming", "Java Programming", "JavaScript Programming", "AI & Machine Learning", "Data Science"]
    return render_template('dashboard.html', user=user, recommendations=recommendations)

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
    cursor.execute("SELECT name, skills FROM users WHERE skills LIKE %s OR name LIKE %s", (f"%{query}%", f"%{query}%"))
    results = cursor.fetchall()
    return render_template('search.html', results=results)

@app.route('/send_request/<int:receiver_id>')
def send_request(receiver_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    cursor.execute("INSERT INTO requests (sender_id, receiver_id) VALUES (%s, %s)", (session['user_id'], receiver_id))
    db.commit()
    return redirect(url_for('home'))

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

if __name__ == '__main__':
    app.run(debug=True)

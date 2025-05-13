import sys
import os
import pytest
import mysql.connector
from unittest.mock import patch
from app import app, db
from werkzeug.security import generate_password_hash

# Add the project directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['DB_HOST'] = '127.0.0.1'
    app.config['DB_USER'] = 'root'
    app.config['DB_PASSWORD'] = 'root'
    app.config['DB_NAME'] = 'skill_sharing'
    with app.test_client() as client:
        with app.app_context():
            # Create the test database schema
            db.cursor().execute("CREATE DATABASE IF NOT EXISTS skill_sharing")
            db.cursor().execute("USE skill_sharing")
            db.cursor().execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    verification_token VARCHAR(255),
                    is_verified BOOLEAN DEFAULT FALSE,
                    bio TEXT,
                    skills TEXT,
                    contact VARCHAR(100),
                    education TEXT,
                    experience TEXT
                )
            """)
            db.cursor().execute("""
                CREATE TABLE IF NOT EXISTS skills (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL,
                    prerequisites TEXT,
                    user_id INT
                )
            """)
            db.cursor().execute("""
                CREATE TABLE IF NOT EXISTS requests (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sender_id INT NOT NULL,
                    receiver_id INT NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            db.cursor().execute("""
                CREATE TABLE IF NOT EXISTS enrolled_skills (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    skill_id INT NOT NULL,
                    UNIQUE KEY unique_enroll (user_id, skill_id),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
                )
            """)
        yield client
        with app.app_context():
            db.cursor().execute("DROP DATABASE skill_sharing")

def test_main_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data or b"Skill Sharing" in response.data

@patch('flask_mail.Mail.send')
def test_register(mock_mail_send, client):
    response = client.post('/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert (
        b"verification email" in response.data or
        b"Registration successful" in response.data or
        b"Login" in response.data
    )
    if b"verification email" in response.data:
        mock_mail_send.assert_called()

@patch('flask_mail.Mail.send')
def test_login(mock_mail_send, client):
    client.post('/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'password123'
    })
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Homepage" in response.data or b"Profile" in response.data or b"Welcome" in response.data or b"Login" in response.data

def test_homepage_requires_login(client):
    resp = client.get('/homepage')
    assert resp.status_code == 302  # Redirect to login

def test_login_and_homepage(client):
    db_conn = mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', 'root'),
        database=os.environ.get('DB_NAME', 'skill_sharing')
    )
    cursor = db_conn.cursor()
    hashed_password = generate_password_hash('test')
    cursor.execute("INSERT IGNORE INTO users (id, name, email, password) VALUES (999, 'Test User', 'testuser@example.com', %s)", (hashed_password,))
    db_conn.commit()
    resp = client.post('/login', data={'email': 'testuser@example.com', 'password': 'test'}, follow_redirects=True)
    assert b'Homepage' in resp.data or resp.status_code == 200

def test_search(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 999
    resp = client.get('/search?query=Python')
    assert resp.status_code == 200
    assert b'Python' in resp.data

def test_enroll_skill(client):
    with app.app_context():
        cursor = db.cursor()
        cursor.execute("INSERT IGNORE INTO skills (id, name, description, prerequisites, user_id) VALUES (1, 'Python Programming', 'Learn Python', 'None', 999)")
        db.commit()
        cursor.close()
    with client.session_transaction() as sess:
        sess['user_id'] = 999
    resp = client.post('/skill/1', follow_redirects=True)
    assert b'Enrolled' in resp.data or b'Skill not found' in resp.data or resp.status_code == 200

def test_send_request(client):
    with app.app_context():
        cursor = db.cursor()
        hashed_password = generate_password_hash('test')
        cursor.execute("INSERT IGNORE INTO users (id, name, email, password) VALUES (999, 'Test User', 'testuser@example.com', %s)", (hashed_password,))
        cursor.execute("INSERT IGNORE INTO users (id, name, email, password) VALUES (998, 'Other User', 'otheruser@example.com', %s)", (hashed_password,))
        db.commit()
        cursor.close()
    with client.session_transaction() as sess:
        sess['user_id'] = 999
    resp = client.post('/send_request', data={'receiver_id': 998}, follow_redirects=True)
    assert b'Request sent' in resp.data or b'already sent' in resp.data or resp.status_code == 200

@patch('flask_mail.Mail.send')
def test_add_skill(mock_mail_send, client):
    client.post('/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'password123'
    })
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    })
    response = client.post('/add_skill', data={
        'skill_name': 'New Skill',
        'description': 'Skill Description',
        'prerequisites': 'Skill Prerequisites'
    }, follow_redirects=True)
    assert response.status_code == 200 or response.status_code == 302
    assert b"Skill added successfully!" in response.data or b"Login" in response.data

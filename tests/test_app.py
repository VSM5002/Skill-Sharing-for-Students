import sys
import os
import pytest
from unittest.mock import patch
from app import app, db

# Add the project directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['DB_HOST'] = '127.0.0.1'
    app.config['DB_USER'] = 'test_user'
    app.config['DB_PASSWORD'] = 'test_password'
    app.config['DB_NAME'] = 'test_db'
    with app.test_client() as client:
        with app.app_context():
            # Create the test database schema
            db.cursor().execute("CREATE DATABASE IF NOT EXISTS test_db")
            db.cursor().execute("USE test_db")
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
                    prerequisites TEXT
                )
            """)
            db.cursor().execute("""
                CREATE TABLE IF NOT EXISTS user_skills (
                    user_id INT NOT NULL,
                    skill_id INT NOT NULL,
                    PRIMARY KEY (user_id, skill_id),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
                )
            """)
            db.cursor().execute("""
                CREATE TABLE IF NOT EXISTS requests (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sender_id INT NOT NULL,
                    receiver_id INT NOT NULL,
                    FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
        yield client
        with app.app_context():
            # Drop the test database after tests
            db.cursor().execute("DROP DATABASE test_db")

def test_main_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data  # Adjust based on your main.html content

@patch('flask_mail.Mail.send')  # Mock the Mail.send method
def test_register(mock_mail_send, client):
    response = client.post('/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"verification email" in response.data
    mock_mail_send.assert_called_once()  # Ensure the email send method was called

@patch('flask_mail.Mail.send')  # Mock the Mail.send method
def test_login(mock_mail_send, client):
    # First, register a user
    client.post('/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'password123'
    })
    # Then, log in with the same user
    response = client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Dashboard" in response.data  # Adjust based on your dashboard.html content

@patch('flask_mail.Mail.send')  # Mock the Mail.send method
def test_dashboard(mock_mail_send, client):
    # Log in first
    client.post('/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'password123'
    })
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    })
    # Access dashboard
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b"Recommendations" in response.data

@patch('flask_mail.Mail.send')  # Mock the Mail.send method
def test_logout(mock_mail_send, client):
    # Log in first
    client.post('/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'password123'
    })
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    })
    # Log out
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome" in response.data

@patch('flask_mail.Mail.send')  # Mock the Mail.send method
def test_forgot_password(mock_mail_send, client):
    # Register a user
    with patch('flask_mail.Mail.send'):  # Mock email sending during registration
        client.post('/register', data={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123'
        })
    # Request password reset
    response = client.post('/forgot_password', data={
        'email': 'test@example.com'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"password reset link" in response.data
    # Ensure the email send method was called exactly once during password reset
    assert mock_mail_send.call_count == 1, f"Expected 1 email to be sent, but {mock_mail_send.call_count} were sent."
    mock_mail_send.reset_mock()  # Reset the mock to avoid interference with other tests

@patch('flask_mail.Mail.send')  # Mock the Mail.send method
def test_search_users(mock_mail_send, client):
    # Log in first
    client.post('/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'password123'
    })
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    })
    # Perform a search
    response = client.post('/search_users', data={
        'query': 'Python'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Python" in response.data  # Adjust based on your search results

@patch('flask_mail.Mail.send')  # Mock the Mail.send method
def test_add_skill(mock_mail_send, client):
    # Log in first
    client.post('/register', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'password123'
    })
    client.post('/login', data={
        'email': 'test@example.com',
        'password': 'password123'
    })
    # Add a skill
    response = client.post('/add_skill', data={
        'skill_name': 'New Skill',
        'description': 'Skill Description',
        'prerequisites': 'Skill Prerequisites'
    }, follow_redirects=True)
    assert response.status_code == 200
    # Print the response data for debugging
    print(response.data.decode('utf-8'))  # Decode the response data to make it human-readable
    # Check if the success message is displayed in the response
    assert b"Skill added successfully!" in response.data, f"Expected success message not found in response: {response.data}"
    # Ensure the cursor is properly closed before executing the next query
    cursor = db.cursor()  # Create a new cursor
    cursor.execute("SELECT * FROM skills WHERE name = %s", ('New Skill',))
    skill = cursor.fetchone()
    cursor.close()  # Close the cursor to avoid unread result errors
    assert skill is not None, "Skill was not added to the database."
    assert skill[1] == 'New Skill'  # Check the skill name
    assert skill[2] == 'Skill Description'  # Check the description
    assert skill[3] == 'Skill Prerequisites'  # Check the prerequisites

# Skill Sharing Platform

A web application that allows users to share and learn skills. Users can register, create profiles, search for skills, send skill-sharing requests, and manage their accounts.

## Features

1. **User Registration and Login**:
   - Secure registration with email verification.
   - Login with email and password.
   - Forgot password functionality with email-based password reset.

2. **Profile Management**:
   - Create and edit profiles with fields like bio, skills, education, and experience.
   - Track profile completion percentage.

3. **Skill Search**:
   - Search for users by skill name or user name.

4. **Skill Recommendations**:
   - Dashboard displays recommended courses with images.

5. **Skill-Sharing Requests**:
   - Send and manage skill-sharing requests.

6. **Account Management**:
   - Delete account from the settings page.

7. **Responsive UI**:
   - Clean and responsive design for all pages.

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MySQL
- **Email Service**: Flask-Mail (SMTP with Gmail)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd skill-sharing-platform
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database:
   - Create a MySQL database named `skill_sharing`.
   - Run the following SQL commands to create the required tables:
     ```sql
     CREATE TABLE users (
         id INT AUTO_INCREMENT PRIMARY KEY,
         name VARCHAR(100),
         email VARCHAR(100) UNIQUE,
         password VARCHAR(255),
         bio TEXT,
         skills TEXT,
         contact VARCHAR(100),
         education TEXT,
         experience TEXT,
         verification_token VARCHAR(255),
         is_verified BOOLEAN DEFAULT FALSE
     );

     CREATE TABLE requests (
         id INT AUTO_INCREMENT PRIMARY KEY,
         sender_id INT,
         receiver_id INT,
         FOREIGN KEY (sender_id) REFERENCES users(id),
         FOREIGN KEY (receiver_id) REFERENCES users(id)
     );
     ```

4. Configure email settings:
   - Update the email configuration in `app.py`:
     ```python
     app.config['MAIL_SERVER'] = 'smtp.gmail.com'
     app.config['MAIL_PORT'] = 587
     app.config['MAIL_USE_TLS'] = True
     app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
     app.config['MAIL_PASSWORD'] = 'your_app_password'
     ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Open the application in your browser:
   ```
   http://127.0.0.1:5000/
   ```

## Project Structure

```
skill-sharing-platform/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── dashboard.html
│   ├── forgot_password.html
│   ├── reset_password.html
│   └── settings.html
├── static/                # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
└── README.md              # Project documentation
```

## Usage

1. **Register**:
   - Create an account by providing your name, email, and password.

2. **Verify Email**:
   - Check your email for a verification link and click it to verify your account.

3. **Login**:
   - Log in using your registered email and password.

4. **Complete Profile**:
   - Add details like bio, skills, education, and experience.

5. **Search for Skills**:
   - Use the search bar to find users by skill name or user name.

6. **Send Skill-Sharing Requests**:
   - Visit a user's profile and send a skill-sharing request.

7. **Manage Account**:
   - Edit your profile or delete your account from the settings page.

## Troubleshooting

- **Email Verification Not Received**:
  - Ensure the email configuration in `app.py` is correct.
  - Check your spam or promotions folder.

- **Database Connection Issues**:
  - Verify the MySQL server is running and the credentials in `app.py` are correct.

- **SMTP Authentication Error**:
  - Ensure you have enabled "App Passwords" in your Google account.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

- Flask documentation: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
- Flask-Mail documentation: [https://pythonhosted.org/Flask-Mail/](https://pythonhosted.org/Flask-Mail/)
- MySQL documentation: [https://dev.mysql.com/doc/](https://dev.mysql.com/doc/)
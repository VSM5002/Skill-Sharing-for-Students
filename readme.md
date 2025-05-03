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
   - Accept or decline incoming requests.

6. **Account Management**:
   - Delete account from the settings page.
   - Update email and password.

7. **Responsive UI**:
   - Clean and responsive design for all pages.

8. **Notifications**:
   - Receive notifications for skill-sharing requests and updates.

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Database**: MySQL
- **Email Service**: Flask-Mail (SMTP with Gmail)
- **Authentication**: JWT (JSON Web Tokens)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd skill-sharing-platform
   ```

2. Set up a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
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
         status ENUM('pending', 'accepted', 'declined') DEFAULT 'pending',
         FOREIGN KEY (sender_id) REFERENCES users(id),
         FOREIGN KEY (receiver_id) REFERENCES users(id)
     );

     CREATE TABLE notifications (
         id INT AUTO_INCREMENT PRIMARY KEY,
         user_id INT,
         message TEXT,
         is_read BOOLEAN DEFAULT FALSE,
         FOREIGN KEY (user_id) REFERENCES users(id)
     );
     ```

5. Configure environment variables:
   - Create a `.env` file in the root directory and add the following:
     ```
     MAIL_SERVER=smtp.gmail.com
     MAIL_PORT=587
     MAIL_USE_TLS=True
     MAIL_USERNAME=your_email@gmail.com
     MAIL_PASSWORD=your_app_password
     SECRET_KEY=your_secret_key
     DATABASE_URI=mysql+pymysql://username:password@localhost/skill_sharing
     ```

6. Run the application:
   ```bash
   python app.py
   ```

7. Open the application in your browser:
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
│   ├── notifications.html
│   └── settings.html
├── static/                # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
├── .env                   # Environment variables
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

7. **Manage Requests**:
   - Accept or decline incoming skill-sharing requests.

8. **Notifications**:
   - View notifications for updates and requests.

9. **Manage Account**:
   - Edit your profile, update email/password, or delete your account from the settings page.

## Troubleshooting

- **Email Verification Not Received**:
  - Ensure the email configuration in `.env` is correct.
  - Check your spam or promotions folder.

- **Database Connection Issues**:
  - Verify the MySQL server is running and the credentials in `.env` are correct.

- **SMTP Authentication Error**:
  - Ensure you have enabled "App Passwords" in your Google account.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Make your changes and commit them (`git commit -m "Add feature-name"`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

- Flask documentation: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
- Flask-Mail documentation: [https://pythonhosted.org/Flask-Mail/](https://pythonhosted.org/Flask-Mail/)
- MySQL documentation: [https://dev.mysql.com/doc/](https://dev.mysql.com/doc/)
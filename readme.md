# Skill Sharing Platform

A web platform for students to share and learn skills from each other.

## Features

- User registration and login with college email verification
- Profile management and skill enrollment
- Add and search for skills and users
- Request and accept skill sharing connections
- Track certificates and completed courses
- Email verification and notifications
- Modern, warm-themed UI (red/orange/white)

## Tech Stack

- Python (Flask)
- MySQL
- HTML/CSS (warm color palette)
- Flask-Mail for email
- GitHub Actions for CI

## Setup

1. **Clone the repository**
2. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```
3. **Set up environment variables**  
   Create a `.env` file with your DB and mail settings:
   ```
   FLASK_SECRET_KEY=your_secret_key
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=yourpassword
   DB_NAME=skill_sharing
   MAIL_SERVER=smtp.yourmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your@email.com
   MAIL_PASSWORD=yourpassword
   ALLOWED_EMAIL_DOMAIN=yourcollege.edu
   ```
4. **Set up the database**
   - Import `skillshare.sql` into your MySQL server.
   - Make sure the tables for users, skills, enrolled_skills, requests, certificates, etc. exist.

5. **Run the app**
   ```
   python app.py
   ```

6. **Access the app**
   - Open [http://localhost:5000](http://localhost:5000) in your browser.

## UI/UX

- The platform uses a warm color palette (red, orange, white) for a modern, inviting look.
- All pages are styled for clarity and ease of use.
- Sidebar navigation is consistent across main pages.

## Testing

- Automated tests run via GitHub Actions on each push to `master`.
- To run tests locally:
  ```
  pytest tests/test_app.py
  ```

## Contribution

Pull requests are welcome! Please open an issue first to discuss changes.

---

© 2023 Skill Sharing Platform
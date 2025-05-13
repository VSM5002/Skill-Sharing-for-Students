#CREATE DATABASE skill_sharing;

USE skill_sharing;
SHOW tables;
/*
Describe requests;
SELECT * FROM requests;
Describe skills ;
SELECT * FROM skills;
Describe user_skills;
SELECT * FROM user_skills;
Describe users;
SELECT * FROM users;

-- Start inserting from id 10 to avoid conflicts with existing ids (3-9 are already used)
INSERT INTO users (
    id, name, email, password, bio, skills, contact, education, experience, verification_token, is_verified
) VALUES
(10, 'Frank White', 'frank@example.com', 'password123', 'Photographer', 'Photography', '1234567895', 'Diploma in Photography', '7 years', NULL, 1),
(11, 'Grace Green', 'grace@example.com', 'password123', 'Video Editor', 'Video Editing', '1234567896', 'Diploma in Video Editing', '4 years', NULL, 1),
(12, 'Hank Black', 'hank@example.com', 'password123', 'Public Speaker', 'Public Speaking', '1234567897', 'BA in Communications', '8 years', NULL, 1),
(13, 'Ivy Blue', 'ivy@example.com', 'password123', 'Chef', 'Cooking', '1234567898', 'Diploma in Culinary Arts', '10 years', NULL, 1),
(14, 'Jack Red', 'jack@example.com', 'password123', 'Yoga Instructor', 'Yoga', '1234567899', 'Certified Yoga Trainer', '6 years', NULL, 1),
(15, 'Karen Yellow', 'karen@example.com', 'password123', 'Machine Learning Engineer', 'Machine Learning', '1234567800', 'MSc in AI', '5 years', NULL, 1),
(16, 'Leo Orange', 'leo@example.com', 'password123', 'Blockchain Developer', 'Blockchain', '1234567801', 'BSc in Computer Science', '4 years', NULL, 1),
(17, 'Mia Purple', 'mia@example.com', 'password123', 'Cybersecurity Analyst', 'Cybersecurity', '1234567802', 'MSc in Cybersecurity', '3 years', NULL, 1),
(18, 'Nina Pink', 'nina@example.com', 'password123', 'Cloud Engineer', 'Cloud Computing', '1234567803', 'BSc in IT', '5 years', NULL, 1),
(19, 'Oscar Gray', 'oscar@example.com', 'password123', 'DevOps Engineer', 'DevOps', '1234567804', 'BSc in Computer Science', '6 years', NULL, 1),
(20, 'Paul White', 'paul@example.com', 'password123', 'AI Researcher', 'Artificial Intelligence', '1234567805', 'PhD in AI', '7 years', NULL, 1),
(21, 'Quinn Black', 'quinn@example.com', 'password123', 'Mobile App Developer', 'Mobile App Development', '1234567806', 'BSc in Computer Science', '4 years', NULL, 1),
(22, 'Rachel Green', 'rachel@example.com', 'password123', 'Game Developer', 'Game Development', '1234567807', 'BSc in Game Design', '5 years', NULL, 1),
(23, 'Steve Blue', 'steve@example.com', 'password123', 'Ethical Hacker', 'Ethical Hacking', '1234567808', 'MSc in Cybersecurity', '6 years', NULL, 1),
(24, 'Tina Red', 'tina@example.com', 'password123', 'Robotics Engineer', 'Robotics', '1234567809', 'MSc in Robotics', '5 years', NULL, 1),
(25, 'Uma Yellow', 'uma@example.com', 'password123', '3D Artist', '3D Modeling', '1234567810', 'Diploma in 3D Design', '4 years', NULL, 1),
(26, 'Victor Orange', 'victor@example.com', 'password123', 'UI/UX Designer', 'UI/UX Design', '1234567811', 'BSc in Design', '5 years', NULL, 1),
(27, 'Wendy Purple', 'wendy@example.com', 'password123', 'Big Data Analyst', 'Big Data', '1234567812', 'MSc in Data Science', '6 years', NULL, 1),
(28, 'Xander Pink', 'xander@example.com', 'password123', 'AR Developer', 'Augmented Reality', '1234567813', 'BSc in Computer Science', '4 years', NULL, 1),
(29, 'Yara Gray', 'yara@example.com', 'password123', 'VR Developer', 'Virtual Reality', '1234567814', 'BSc in Computer Science', '5 years', NULL, 1),
(30, 'Zane White', 'zane@example.com', 'password123', 'E-commerce Specialist', 'E-commerce', '1234567815', 'MBA in Marketing', '6 years', NULL, 1),
(31, 'Amy Black', 'amy@example.com', 'password123', 'Content Writer', 'Content Writing', '1234567816', 'BA in English', '5 years', NULL, 1),
(32, 'Brian Green', 'brian@example.com', 'password123', 'Animator', 'Animation', '1234567817', 'Diploma in Animation', '4 years', NULL, 1),
(33, 'Cathy Blue', 'cathy@example.com', 'password123', 'Music Producer', 'Music Production', '1234567818', 'Diploma in Music Production', '6 years', NULL, 1),
(34, 'David Red', 'david@example.com', 'password123', 'Fitness Trainer', 'Fitness Training', '1234567819', 'Certified Fitness Trainer', '7 years', NULL, 1);
*/

/*INSERT INTO skills (id, name, description, prerequisites, user_id) VALUES
(1, 'Python Programming', 'Learn the basics of Python programming.', 'Basic programming knowledge', 3),
(2, 'Web Development', 'Build modern websites using HTML, CSS, and JavaScript.', 'Basic computer skills', 4),
(3, 'Data Science', 'Analyze data and build machine learning models.', 'Statistics and Python', 5),
(4, 'Graphic Design', 'Create stunning visuals using design tools.', 'Creativity and design tools', 6),
(5, 'Digital Marketing', 'Learn SEO, social media marketing, and more.', 'Basic marketing knowledge', 7),
(6, 'Photography', 'Master the art of capturing stunning photos.', 'Camera and photography basics', 10),
(7, 'Video Editing', 'Learn to edit videos like a pro.', 'Basic video editing tools', 11),
(8, 'Public Speaking', 'Enhance your communication and presentation skills.', 'Confidence and communication skills', 12),
(9, 'Cooking', 'Learn to cook delicious meals.', 'Basic cooking tools', 13),
(10, 'Yoga', 'Improve your flexibility and mental health.', 'Yoga mat and comfortable clothing', 14),
(11, 'Machine Learning', 'Learn to build predictive models using data.', 'Python and statistics', 15),
(12, 'Blockchain', 'Understand the fundamentals of blockchain technology.', 'Basic programming knowledge', 16),
(13, 'Cybersecurity', 'Protect systems and networks from cyber threats.', 'Networking basics', 17),
(14, 'Cloud Computing', 'Learn to deploy and manage applications in the cloud.', 'Basic IT knowledge', 18),
(15, 'DevOps', 'Master CI/CD pipelines and automation tools.', 'Basic programming and IT knowledge', 19),
(16, 'Artificial Intelligence', 'Explore AI concepts and applications.', 'Python and mathematics', 20),
(17, 'Mobile App Development', 'Create mobile apps for Android and iOS.', 'Basic programming knowledge', 21),
(18, 'Game Development', 'Design and develop engaging video games.', 'Programming and creativity', 22),
(19, 'Ethical Hacking', 'Learn to identify and fix security vulnerabilities.', 'Networking and cybersecurity basics', 23),
(20, 'Robotics', 'Build and program robots for various tasks.', 'Programming and electronics', 24),
(21, '3D Modeling', 'Create 3D models for games and animations.', 'Creativity and 3D tools', 25),
(22, 'UI/UX Design', 'Design user-friendly interfaces and experiences.', 'Creativity and design tools', 26),
(23, 'Big Data', 'Analyze and process large datasets efficiently.', 'Statistics and programming', 27),
(24, 'Augmented Reality', 'Create immersive AR experiences.', 'Programming and creativity', 28),
(25, 'Virtual Reality', 'Develop VR applications and simulations.', 'Programming and creativity', 29),
(26, 'E-commerce', 'Build and manage online stores.', 'Basic business knowledge', 30),
(27, 'Content Writing', 'Write engaging and impactful content.', 'Creativity and writing skills', 31),
(28, 'Animation', 'Create stunning animations for videos and games.', 'Creativity and animation tools', 32),
(29, 'Music Production', 'Compose and produce music tracks.', 'Creativity and music tools', 33),
(30, 'Fitness Training', 'Learn to stay fit and healthy.', 'Basic fitness knowledge', 34);
*/
-- If you encounter "Lost connection" or foreign key errors, try disabling foreign key checks temporarily:
SET FOREIGN_KEY_CHECKS = 0;

-- Use only the enrolled_skills table for tracking skill enrollments.
CREATE TABLE IF NOT EXISTS enrolled_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    skill_id INT NOT NULL,
    UNIQUE KEY unique_enroll (user_id, skill_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

describe enrolled_skills;

-- The required columns already exist in your 'requests' and 'skills' tables.
-- You can safely remove or comment out any ALTER TABLE statements for 'user_id', 'status', or 'timestamp' to avoid errors.

-- If you are still getting "Unknown column" errors in your tests:
-- 1. Double-check that your test database (test_db) has the same schema as your main database.
-- 2. Re-run your schema SQL on the test database:
--    mysql -u root -p test_db < skillshare.sql
-- 3. If using CI/CD, ensure the schema is loaded before running tests.

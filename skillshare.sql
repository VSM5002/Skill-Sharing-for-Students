#CREATE DATABASE skill_sharing;

USE skill_sharing;
SHOW tables;

Describe requests;
Describe skills;
Describe user_skills;
Describe users;

-- Add the image_url column to the skills table
ALTER TABLE skills ADD COLUMN image_url VARCHAR(255);

-- Example: Insert skills with image URLs
INSERT INTO skills (name, description, image_url) VALUES
('Python Programming', 'Learn the basics of Python programming.', 'https://example.com/images/python.jpg'),
('Web Development', 'Build modern websites using HTML, CSS, and JavaScript.', 'https://example.com/images/webdev.jpg'),
('Data Science', 'Analyze data and build machine learning models.', 'https://example.com/images/datascience.jpg'),
('Graphic Design', 'Create stunning visuals using design tools.', 'https://example.com/images/graphicdesign.jpg'),
('Digital Marketing', 'Learn SEO, social media marketing, and more.', 'https://example.com/images/digitalmarketing.jpg');

SELECT * FROM users;
SELECT * FROM skills;
SELECT * FROM user_skills;
SELECT * FROM requests;

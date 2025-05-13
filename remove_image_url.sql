USE skill_sharing;

CREATE TABLE IF NOT EXISTS enrolled_skills (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    skill_id INT NOT NULL,
    UNIQUE KEY unique_enroll (user_id, skill_id)
);
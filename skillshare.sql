#CREATE DATABASE skill_sharing;

USE skill_sharing;

/*CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    bio TEXT,
    skills TEXT,
    contact VARCHAR(100)
);

CREATE TABLE requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT,
    receiver_id INT,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id)
);*/

Select * from users;
Select * from requests;

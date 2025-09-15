-- Drop database if it exists
DROP DATABASE IF EXISTS CCCS105;

-- Create database
CREATE DATABASE IF NOT EXISTS CCCS105;
-- Use database
USE CCCS105;

CREATE TABLE IF NOT EXISTS admins (
    admin_id INT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- Insert default admin (password: admin123)
INSERT INTO admins (admin_id, username, password_hash)
VALUES (1, 'admin', SHA2('admin123', 256));

-- Receptionist Users
CREATE TABLE IF NOT EXISTS receptionists (
    receptionist_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- By default there is one receptionist with the following credentials:
-- username: receptionist
-- password: receptionist123
INSERT INTO receptionists (receptionist_id, name, username, password_hash)
VALUES (1, 'Receptionist', 'receptionist', SHA2('receptionist123', 256));


-- Guest Table
CREATE TABLE IF NOT EXISTS guests (
    guest_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    id_document VARCHAR(50) NOT NULL UNIQUE
);

-- Rooms Table
CREATE TABLE IF NOT EXISTS rooms (
    room_id INT PRIMARY KEY AUTO_INCREMENT,
    room_type VARCHAR(50) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL
);

-- Bookings Table
CREATE TABLE IF NOT EXISTS bookings (
    booking_id INT PRIMARY KEY AUTO_INCREMENT,
    guest_id INT NOT NULL,
    room_id INT NOT NULL,
    check_in DATE NOT NULL, 
    check_out DATE NOT NULL,
    status VARCHAR(50) NOT NULL,
    FOREIGN KEY (guest_id) REFERENCES guests(guest_id),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id)
);

-- Payments Table
CREATE TABLE IF NOT EXISTS payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    booking_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date DATE NOT NULL, 
    method VARCHAR(50) NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
);

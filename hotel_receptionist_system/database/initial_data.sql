-- Use the database
USE CCCS105;

-- Insert rooms with different types and prices
INSERT INTO rooms (room_type, price, status) VALUES
('Standard Single', 100.00, 'vacant'),
('Standard Double', 150.00, 'vacant'),
('Deluxe Single', 200.00, 'vacant'),
('Deluxe Double', 250.00, 'vacant'),
('Suite', 350.00, 'vacant'),
('Presidential Suite', 500.00, 'vacant'),
('Family Room', 300.00, 'vacant'),
('Ocean View', 275.00, 'vacant'),
('Garden View', 225.00, 'vacant'),
('Executive Suite', 450.00, 'vacant'),
('Penthouse', 600.00, 'vacant'),
('Budget Single', 80.00, 'vacant');

-- Insert sample guests
INSERT INTO guests (name, phone, email, id_document) VALUES
('John Smith', '+1234567890', 'john.smith@email.com', 'PASS123456'),
('Mary Johnson', '+1987654321', 'mary.j@email.com', 'DL789012'),
('Robert Brown', '+1122334455', 'robert.b@email.com', 'ID345678'),
('Sarah Wilson', '+1555666777', 'sarah.w@email.com', 'PASS987654'),
('Michael Davis', '+1999888777', 'michael.d@email.com', 'DL112233'),
('Emma Thompson', '+1444555666', 'emma.t@email.com', 'PASS456789'),
('David Garcia', '+1333222111', 'david.g@email.com', 'ID654321'),
('Jennifer Lee', '+1777888999', 'jennifer.l@email.com', 'DL987654'),
('William Chen', '+1222333444', 'william.c@email.com', 'PASS135790'),
('Olivia Rodriguez', '+1666777888', 'olivia.r@email.com', 'ID246810');

-- Insert receptionists
INSERT INTO receptionists (name, username, password_hash) VALUES
('Mark Joseph Orias', 'maorias', SHA2('maorias123', 256)),
('John Raymond Alba', 'joalba', SHA2('joalba123', 256)),
('Kenji Nathaniel David', 'kdavid', SHA2('kdavid123', 256)),
('Ivy Doroin', 'ivydoroin', SHA2('ivydoroin123', 256)),
('Maria Santos', 'msantos', SHA2('msantos123', 256)),
('James Wilson', 'jwilson', SHA2('jwilson123', 256)),
('Anna Park', 'apark', SHA2('apark123', 256)),
('Carlos Mendoza', 'cmendoza', SHA2('cmendoza123', 256)),
('Lisa Wong', 'lwong', SHA2('lwong123', 256)),
('Daniel Kim', 'dkim', SHA2('dkim123', 256));

-- Insert historical bookings (Checked Out)
INSERT INTO bookings (guest_id, room_id, check_in, check_out, status) VALUES
(1, 1, DATE_SUB(CURDATE(), INTERVAL 10 DAY), DATE_SUB(CURDATE(), INTERVAL 8 DAY), 'Checked Out'),
(2, 2, DATE_SUB(CURDATE(), INTERVAL 9 DAY), DATE_SUB(CURDATE(), INTERVAL 7 DAY), 'Checked Out'),
(3, 3, DATE_SUB(CURDATE(), INTERVAL 7 DAY), DATE_SUB(CURDATE(), INTERVAL 5 DAY), 'Checked Out'),
(4, 4, DATE_SUB(CURDATE(), INTERVAL 15 DAY), DATE_SUB(CURDATE(), INTERVAL 12 DAY), 'Checked Out'),
(5, 5, DATE_SUB(CURDATE(), INTERVAL 20 DAY), DATE_SUB(CURDATE(), INTERVAL 18 DAY), 'Checked Out'),
(6, 6, DATE_SUB(CURDATE(), INTERVAL 25 DAY), DATE_SUB(CURDATE(), INTERVAL 22 DAY), 'Checked Out'),
(7, 7, DATE_SUB(CURDATE(), INTERVAL 30 DAY), DATE_SUB(CURDATE(), INTERVAL 28 DAY), 'Checked Out');

-- Insert current active bookings (Checked In)
INSERT INTO bookings (guest_id, room_id, check_in, check_out, status) VALUES
(4, 4, DATE_SUB(CURDATE(), INTERVAL 2 DAY), DATE_ADD(CURDATE(), INTERVAL 1 DAY), 'Checked In'),
(5, 5, DATE_SUB(CURDATE(), INTERVAL 1 DAY), DATE_ADD(CURDATE(), INTERVAL 2 DAY), 'Checked In'),
(6, 8, DATE_SUB(CURDATE(), INTERVAL 3 DAY), DATE_ADD(CURDATE(), INTERVAL 1 DAY), 'Checked In'),
(7, 9, DATE_SUB(CURDATE(), INTERVAL 2 DAY), DATE_ADD(CURDATE(), INTERVAL 3 DAY), 'Checked In'),
(8, 10, DATE_SUB(CURDATE(), INTERVAL 1 DAY), DATE_ADD(CURDATE(), INTERVAL 4 DAY), 'Checked In');

-- Insert future bookings (Confirmed)
INSERT INTO bookings (guest_id, room_id, check_in, check_out, status) VALUES
(1, 6, DATE_ADD(CURDATE(), INTERVAL 1 DAY), DATE_ADD(CURDATE(), INTERVAL 3 DAY), 'Confirmed'),
(2, 1, DATE_ADD(CURDATE(), INTERVAL 2 DAY), DATE_ADD(CURDATE(), INTERVAL 4 DAY), 'Confirmed'),
(3, 11, DATE_ADD(CURDATE(), INTERVAL 3 DAY), DATE_ADD(CURDATE(), INTERVAL 6 DAY), 'Confirmed'),
(9, 12, DATE_ADD(CURDATE(), INTERVAL 4 DAY), DATE_ADD(CURDATE(), INTERVAL 7 DAY), 'Confirmed'),
(10, 7, DATE_ADD(CURDATE(), INTERVAL 5 DAY), DATE_ADD(CURDATE(), INTERVAL 8 DAY), 'Confirmed');

-- Insert cancelled booking
INSERT INTO bookings (guest_id, room_id, check_in, check_out, status) VALUES
(3, 2, DATE_ADD(CURDATE(), INTERVAL 5 DAY), DATE_ADD(CURDATE(), INTERVAL 7 DAY), 'Cancelled'),
(4, 3, DATE_ADD(CURDATE(), INTERVAL 6 DAY), DATE_ADD(CURDATE(), INTERVAL 9 DAY), 'Cancelled'),
(5, 4, DATE_ADD(CURDATE(), INTERVAL 7 DAY), DATE_ADD(CURDATE(), INTERVAL 10 DAY), 'Cancelled'),
(6, 5, DATE_ADD(CURDATE(), INTERVAL 8 DAY), DATE_ADD(CURDATE(), INTERVAL 11 DAY), 'Cancelled'),
(7, 6, DATE_ADD(CURDATE(), INTERVAL 9 DAY), DATE_ADD(CURDATE(), INTERVAL 12 DAY), 'Cancelled');

-- Insert payments for all bookings
INSERT INTO payments (booking_id, amount, payment_date, method) VALUES
(1, 200.00, DATE_SUB(CURDATE(), INTERVAL 10 DAY), 'Credit Card'),
(2, 300.00, DATE_SUB(CURDATE(), INTERVAL 9 DAY), 'Cash'),
(3, 400.00, DATE_SUB(CURDATE(), INTERVAL 7 DAY), 'Debit Card'),
(4, 750.00, DATE_SUB(CURDATE(), INTERVAL 15 DAY), 'Credit Card'),
(5, 700.00, DATE_SUB(CURDATE(), INTERVAL 20 DAY), 'Credit Card'),
(6, 1500.00, DATE_SUB(CURDATE(), INTERVAL 25 DAY), 'Cash'),
(7, 600.00, DATE_SUB(CURDATE(), INTERVAL 30 DAY), 'Cash'),
(8, 500.00, DATE_SUB(CURDATE(), INTERVAL 2 DAY), 'Credit Card'),
(9, 700.00, DATE_SUB(CURDATE(), INTERVAL 1 DAY), 'Debit Card'),
(10, 825.00, DATE_SUB(CURDATE(), INTERVAL 3 DAY), 'Debit Card'),
(11, 675.00, DATE_SUB(CURDATE(), INTERVAL 2 DAY), 'Credit Card'),
(12, 1800.00, DATE_SUB(CURDATE(), INTERVAL 1 DAY), 'Cash'),
(13, 1000.00, DATE_SUB(CURDATE(), INTERVAL 1 DAY), 'Credit Card'),
(14, 200.00, DATE_SUB(CURDATE(), INTERVAL 1 DAY), 'Cash'),
(15, 1350.00, DATE_SUB(CURDATE(), INTERVAL 1 DAY), 'Debit Card'),
(16, 240.00, DATE_SUB(CURDATE(), INTERVAL 1 DAY), 'Credit Card'),
(17, 900.00, DATE_SUB(CURDATE(), INTERVAL 1 DAY), 'Debit Card');

-- Update room status based on current bookings
UPDATE rooms r
JOIN bookings b ON r.room_id = b.room_id
SET r.status = CASE 
    WHEN b.status = 'Checked In' THEN 'occupied'
    WHEN b.status = 'Confirmed' THEN 'reserved'
    ELSE r.status
END
WHERE b.status IN ('Checked In', 'Confirmed');

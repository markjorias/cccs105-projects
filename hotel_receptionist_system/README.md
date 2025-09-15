<p align="center">
  <a href="https://youtu.be/aXAFw0nssjU" style="text-decoration:none; color:inherit; font-size:16px;">
    <img height="30" width="30" src="https://cdn.simpleicons.org/youtube/ff0000" style="vertical-align:middle; margin-right:6px;"/>
    Full Project Walkthrough
  </a>
</p>

<p align="center">
  <img src="hotel_receptionist_system\documentation\screenshots\login.png" alt="Login" width="250" style="margin-right:10px;"/>
  <img src="hotel_receptionist_system\documentation\screenshots\home.png" alt="Home" width="250"/>
</p>

# Hotel Receptionist System

<p align="center"><em>Final Project in CCCS105: Information Management 1</em></p>

A database application designed to support local hotel front desk operations. It helps receptionists to manage check-ins and check-outs, guests, room availability searches, and payment procedures.

## Repository Details

**Purpose**: Streamline hotel management operations by providing a centralized platform for receptionists and administrators.

**Key Features**:

- **Room management** - Track room availability and types
- **Booking system** - Handle guest reservations and room assignments
- **Guest management** - Store and manage guest information
- **Payment tracking** - Record and monitor payment transactions
- **Multi-user system** - Separate admin and receptionist access levels
- **Data security** - Secure password hashing and protected routes

**Technology Stack**:

- **Backend**: Flask, SQLAlchemy
- **Database**: MySQL via XAMPP
- **Frontend**: Bootstrap, HTML/CSS, JavaScript
- **Authentication**: Session-based login with role separation
- **Security**: SHA-256 password hashing

**Target Users**: Hotel receptionists, hotel owners / managers (admin) that need a straightforward system to manage daily operations.

# Features

- Room availability tracking
- Guest registration and management
- Booking creation and modification
- Payment recording
- Admin and receptionist dashboards
- Responsive design

# Prerequisites

- Python 3.6 or higher
- XAMPP with MySQL
- pip (Python package manager)

# Setup

1. **Clone or download this repository**

2. **Install the required Python packages**
   pip install flask flask-sqlalchemy mysql-connector-python python-dotenv werkzeug

3. **Set up the database**

- Start XAMPP and ensure MySQL service is running
- Run the database creation script:
  `python create_database.py`
- Or manually import schema.sql through phpMyAdmin
- (Optional) Import `initial_data.sql` through phpMyAdmin

4. **Set up environment variables**

- Create a `.env` file in the root directory with the following content:

## Flask configuration

`SECRET_KEY="groupthree"`

## Database configuration

```
DB_USER=root
DB_PASSWORD=""
DB_HOST=localhost
DB_PORT=3306
DB_NAME=CCCS105
```

- Replace `"groupthree"` with a secure random string
- Replace `""` with your MySQL password

5. **Run the application**

python run.py

6. **Access the application**
   The application will be available at `http://127.0.0.1:5000/`

Admin access:

- Username: `admin`
- Password: `admin123`

Receptionist access:

- Username: `receptionist`
- Password: `receptionist123`

## Project Folder Structure:

```
├── database/
│   ├── initial_data.sql
│   └── schema.sql
├── documentation/
│   ├── diagrams/
│   │   ├── erd.png
│   │   └── rm.png
│   └── documentation.pdf
├── source_code/
│   ├── app/
│   │   ├── static/
│   │   │   ├── main.js
│   │   │   └── style.css
│   │   ├── templates/
│   │   │   ├── admin/
│   │   │   │   ├── add_receptionist.html
│   │   │   │   ├── add_rooms.html
│   │   │   │   └── dashboard.html
│   │   │   ├── base.html
│   │   │   ├── bookings.html
│   │   │   ├── check_in.html
│   │   │   ├── check_out.html
│   │   │   ├── edit_guest.html
│   │   │   ├── home.html
│   │   │   ├── login.html
│   │   │   └── manage_guest.html
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── models.py
│   │   └── routes.py
│   ├── .env
│   ├── create_database.py
│   ├── requirements.txt
│   └── run.py
├── README.txt
```

## Troubleshooting

If you encounter database connection issues:

1. Check if XAMPP's MySQL service is running
2. Verify MySQL username and password in `.env`
3. Test the database connection by visiting `http://127.0.0.1:5000/dbtest`
4. Make sure the CCCS105 database exists in MySQL

# Business Rules

### Room Type and Price Definition

**Constraints**

1. Price must be a positive decimal value greater than 0.
2. Only the administrator can add new rooms.

**Conditions**

1. A room cannot be created without both type and price specified.
2. A room cannot be deleted once occupied or has a booking history.
3. Price changes require an administrator.

### Room Status Tracking

**Constraints**

1. Status must be one of: Vacant, Reserved, Occupied

**Conditions**

1. The room status will be updated once a guest books the room, checks in, or checks out.

### Booking Overlap Prevention

**Constraints**

1. No two confirmed bookings can overlap for the same room.
2. The system must check availability in real-time before confirmation.
3. Past dates cannot be selected for new bookings.

**Conditions**

1. Cancelled bookings immediately free up room availability.

### Booking Status Management

**Constraints**

1. Status must be one of: Confirmed, Checked-In, Checked-Out, and Cancelled.
2. Cancelled bookings can be deleted, but cannot be reactivated (new booking required)

**Conditions**

1. Automatic status updates at check-in/check-out date.
2. Status history must be maintained for audit purposes.

### Guest and Room Association

**Constraints**

1. Every booking must link to exactly one room.

**Conditions**
Guest information must be complete before booking and check-in.

### User Access Management

**Constraints**

1. Receptionists only have limited to booking, check-ins and out, and guest management modules.

**Conditions**

1. Admins have full system access, which includes all modules and functions.

# Database Schema

The system uses the following main tables:

- admins: System administrators
- receptionists: Front desk staff
- guests: Hotel guests
- rooms: Hotel rooms
- bookings: Room reservations
- payments: Transaction records

For detailed schema information, refer to schema.sql

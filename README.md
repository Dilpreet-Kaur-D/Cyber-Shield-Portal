🛡️ CyberShield Portal — A Secure Feedback Management System

CyberShield Portal is a role-based, secure, and user-friendly feedback management system designed for academic institutions.
It enables students, staff, and administrators to submit, view, and manage feedback using a modern GUI (Tkinter + CustomTkinter) and a secure Flask backend.

This project focuses heavily on security, data privacy, authentication, and real-time visualization.

🚀 Features
🔐 Secure Authentication

Password hashing using bcrypt

OTP-based login verification

JWT-based session management

Account lockout after 3 failed attempts

Strict role-based access control (RBAC)

🧑‍🎓 Student Features

Simple and clean feedback submission form

Ratings for: Teaching, Internet, Labs, Infrastructure

Optional suggestions box

Duplicate feedback detection and prevention

👨‍🏫 Staff Features

View feedback only for their department

Real-time charts (Matplotlib)

Tabular feedback display with sorting and scrolling

Fully authenticated using JWT

🛠️ Admin Features

Add staff accounts

Monitor login attempts

Export department-wise feedback (.csv)

View complete feedback analytics

Full role & privilege control

🧰 Security Features

Input sanitization (re module)

OTP verification

JWT token expiry handling

SQL injection protection

Hashed password storage

Token tampering detection

🏗️ System Architecture

CyberShield uses a Client–Server Model:

Frontend (Client)

Tkinter + CustomTkinter GUI

Handles login, feedback, dashboards

Sends requests to backend using requests

Backend (Server)

Flask RESTful API

Handles authentication, storage, validation

Communicates with SQLite database

Database

SQLite for storing:

Users

Feedback

OTPs

Login attempts

🛠️ Technology Stack
Frontend

Python Tkinter

CustomTkinter

Matplotlib

Backend

Flask

SQLite

Security

bcrypt

JWT (PyJWT)

re (sanitization)

Others

requests

datetime

Python Standard Library

📦 Installation
1. Clone the Repository
https://github.com/Dilpreet-Kaur-D/Cyber-Shield-Portal.git
cd Cyber Shield Portal

2. Create & Activate Environment
python -m venv env
env\Scripts\activate

3. Install Dependencies
pip install -r requirements.txt

4. Run the Backend Server
python flask_app.py

5. Run the GUI (Frontend)
python main_login.py


🧪 Testing Summary

✓ Registration & login tested

✓ OTP verification

✓ SQL injection prevention

✓ JWT expiration & tampering handling

✓ UI responsiveness

✓ Role-based access control

🧭 Future Enhancements

Web-based version (Flask/FastAPI + React)

Forgot Password via email OTP

Anti-XSS protection (for web version)

Token blacklisting and advanced session control

Email/SMS OTP instead of console print

Automated analytics using ML

Multilingual UI support

Cloud database integration

📝 Author

Dilpreet Kaur – Developer

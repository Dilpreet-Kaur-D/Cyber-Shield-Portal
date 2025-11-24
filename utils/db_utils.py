# db_utlis....Step 1: Import SQLite3 module
import sqlite3
import time
from datetime import datetime   # For getting current date & time
from utils.security import hash_password, verify_password


# Step 2: Create a connection to the database
def create_connection():
    conn = sqlite3.connect("database.db")  # Creates the database file if it doesn’t exist
    return conn  # Gives back the connection so other functions can use it

# Step 3: Create the tables we need
def create_tables():
    conn = create_connection()  # Step 1: Connect to DB
    cursor = conn.cursor()      # Step 2: Prepare to send SQL commands
#-----------------------------------------------------------------------------------------------------------------------
    # Step 3A: Create 'users' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,   -- Unique user ID
            username TEXT NOT NULL UNIQUE,          -- Username (must be unique)
            password TEXT NOT NULL,                 -- Password (will be hashed )
            role TEXT NOT NULL,                      -- Role: student, staff, or admin
            department TEXT
        )
    ''')
#---------------------------------------------------------------------------------------------------------------------
    # Step 3B: Create 'feedback' table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for each feedback
            username TEXT NOT NULL,                -- Who submitted the feedback
            department TEXT,
            teaching TEXT,                         -- Feedback on teaching
            internet TEXT,                         -- Feedback on internet
            cleanliness TEXT,                      -- Feedback on cleanliness
            labs TEXT,                             -- Feedback on labs
            comments TEXT,                         -- Extra feedback
            submitted_at TEXT                      -- Timestamp (date/time)
        )
    ''')
    
    conn.commit()   # Save changes permanently to the database
    conn.close()    # Close the connection safely

#----------------------------------------------------------------------------------------------------------------------
# Step 5: Register a new user (Insert into 'users' table)
def add_user(username, password, role,department):
    conn = create_connection()  # Connect to DB
    cursor = conn.cursor()      # Get cursor to run SQL

    try:
        #Step 1: Hash the password before storing
        hashed_password = hash_password(password)
        # Insert new user into table
        cursor.execute('''
            INSERT INTO users (username, password, role, department)
            VALUES (?, ?, ?, ?)
        ''', (username, hashed_password, role, department))

        conn.commit()  # Save changes
        return True    # Successfully added

    except sqlite3.IntegrityError:
        # This happens if username already exists (UNIQUE constraint)
        return False

    finally:
        conn.close()  # Always close DB connection
#-----------------------------------------------------------------------------------------------------------------------
# Step 6: Check login details (used in login form)
def check_user(username, password, role):
    conn = create_connection()
    cursor = conn.cursor()
    #Step 1: Get user info by username & role only (don't check password here)
    cursor.execute('''
        SELECT username, role, department, password FROM users
        WHERE username = ? AND role = ?
    ''', (username, role))
    
    result = cursor.fetchone()
    conn.close()

    if result:
        db_username, db_role, db_department, hashed_password = result
        try:
            if verify_password(password, hashed_password):
                return {
                    "username": db_username,
                    "role": db_role,
                    "department": db_department
                }
        except ValueError as e:
            print("❌ Invalid password hash or salt format:", e)
            return None

    return None  # if user not found or password invalid

    
#------------------------------------------------------------------------------------------------------------------------
# Step 7: Save student feedback into 'feedback' table
def save_feedback(username,department, teaching, internet, cleanliness, labs, comments):
    conn = create_connection()
    cursor = conn.cursor()

    submitted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 🕒 Current timestamp

    cursor.execute('''
        INSERT INTO feedback (username, department,teaching, internet, cleanliness, labs, comments,submitted_at)
        VALUES (?, ?, ?, ?, ?, ?, ?,?)
    ''', (username,department, teaching, internet, cleanliness, labs, comments, submitted_at))

    conn.commit()
    conn.close()

#---------------------------------------------------------------------------------------------------------------------
#Step 8: View feedback based on role (for staff or admin)
def get_feedback_by_role(role, username=None):
    conn = create_connection()
    cursor = conn.cursor()

    if role == "admin":
        cursor.execute("SELECT * FROM feedback")  # Admin sees all
    elif role == "staff":
        cursor.execute("SELECT * FROM feedback WHERE username = ?", (username,))  # Staff view own students
    else:
        return []  # Students don't get access to view feedback

    results = cursor.fetchall()#list of tuple of records
    conn.close()
    return results  # Returns list of feedback records
#------------------------------------------------------------------------------------------------------------
#Get feedback submitted by students of that department
def get_feedback_by_department(department):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedback WHERE department = ?", (department,))
    results = cursor.fetchall()
    conn.close()
    return results

#----------------------------------------------------------------------------------------------
#  Get the department of that staff
def get_user_department(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT department FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None
#-------------------------------------------------------------------------------------------------
# utils/db_utils.py
def get_all_feedback_averages():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT department,AVG(teaching) AS teaching,AVG(internet) AS internet,AVG(labs) AS labs,AVG(cleanliness) AS infra
        FROM feedback
        GROUP BY department
    """)
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "department": row[0],
            "teaching": row[1],
            "internet": row[2],
            "labs": row[3],
            "infra": row[4]
        })
    return results

#--------------------------------------------------------------

def create_login_log_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            ip_address TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_login_activity(username, role, ip_address):
    conn = create_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO login_activity (username, role, ip_address, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (username, role, ip_address, timestamp))
    conn.commit()
    conn.close()

# ----------------------------------------------
# Brute Force Protection: Global Attempt Tracker
# ----------------------------------------------

# This logic locks the login system after 3 total failed attempts,
# no matter what username, password, or role is tried.
# It protects against brute-force attacks using multiple usernames.

def create_attempts_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attempts (
            username TEXT,
            role TEXT,
            failed_attempts INTEGER DEFAULT 0,
            locked_until TEXT DEFAULT NULL,
            PRIMARY KEY (username, role)
        )
    ''')
    conn.commit()
    conn.close()





#--------------------------------------------------------------------------
from datetime import datetime, timedelta

def get_attempt(username, role):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT failed_attempts, locked_until FROM attempts WHERE username = ? AND role = ?", (username, role))
    row = cursor.fetchone()
    conn.close()
    return row if row else (0, None)

def update_attempt(username, role, failed, locked_until=None):
    conn = create_connection()
    cursor = conn.cursor()
    if locked_until:
        cursor.execute(
            "INSERT OR REPLACE INTO attempts (username, role, failed_attempts, locked_until) VALUES (?, ?, ?, ?)",
            (username, role, failed, locked_until)
        )
    else:
        cursor.execute(
            "INSERT OR REPLACE INTO attempts (username, role, failed_attempts) VALUES (?, ?, ?)",
            (username, role, failed)
        )
    conn.commit()
    conn.close()

def clear_attempt(username, role):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attempts WHERE username = ? AND role = ?", (username, role))
    conn.commit()
    conn.close()

#--------------------------------------------------------
# --- OTP TABLE (one current code per user) -----------------
def create_otp_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS otp_codes (
            username TEXT PRIMARY KEY,
            code     TEXT,
            expires  INTEGER        -- epoch seconds
        )
    """)
    conn.commit()
    conn.close()

# call once at app start
create_otp_table()
def store_otp(username: str, code: str, ttl_secs: int = 120):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO otp_codes (username, code, expires) VALUES (?, ?, ?)",
        (username, code, int(time.time()) + ttl_secs)
    )
    conn.commit(); conn.close()

def verify_and_delete_otp(username: str, code: str) -> bool:
    conn = create_connection(); cursor = conn.cursor()
    cursor.execute("SELECT code, expires FROM otp_codes WHERE username = ?", (username,))
    row = cursor.fetchone(); conn.close()

    if not row:                              # nothing stored
        return False
    saved_code, expires = row
    if code == saved_code and time.time() < expires:
        # success – delete so it can’t be reused
        conn = create_connection(); cur = conn.cursor()
        cur.execute("DELETE FROM otp_codes WHERE username = ?", (username,))
        conn.commit(); conn.close()
        return True
    return False
def get_user_role(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


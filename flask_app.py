from flask import Flask, request, jsonify,render_template,redirect
#request--access incoming data (like form data or JSON) from the client
#jsonify--Converts Python dictionaries → JSON response.. API can send structured responses back (like {"status": "success"}) 
from utils.db_utils import add_user, check_user, save_feedback,get_user_department
import jwt #It allows your app to create and verify JWT tokens.
#jwt.encode(...) → to generate token during login
#jwt.decode(...) → to verify token on protected routes
from config.secret_config import SECRET_KEY #importing the sensitive secret key from outside your main code for safety..
#secrret key is used to sign the token (so no one can fake it)and verify the token later
# -----------------------------------------------------------------------------------------------------------------
from utils.db_utils import get_attempt, update_attempt, clear_attempt
from datetime import datetime, timedelta,timezone
from utils.db_utils import log_login_activity, create_login_log_table,store_otp, verify_and_delete_otp,get_user_role
from utils.security import sanitize_input,generate_otp, send_otp



import sqlite3
app=Flask(__name__) #creating Flask app
#app is object of Flask class...
#Flask(...) : 	Class constructor
#__name__	: A special Python variable.Tells Flask where to look for resources like templates, static files, etc. If you're running the file directly, __name__ == '__main__', and Flask knows this is the main entry point.

@app.route("/") #it is a route decorator
# This message appears in browser..which is written below this
def home():
    return "Cybershield flask API is running..."
#return --send back a message to browser or client(tkinter)
# -----------------------------------------------------------------------------------------------------------------
# 1. USER REGISTRATION ROUTE
@app.route("/register",methods=["POST"])
def Signup():#function that gets called when a POST request hits the /register URL.
    data=request.get_json()
#request is a Flask object used to access incoming data......get_json() reads JSON data sent from the GUI (Tkinter)
    print(f"Registration Attempt: {data}")

    # Step 1: Sanitize input
    username = sanitize_input(data.get("username", ""))
    password = data.get("password", "")

    role = sanitize_input(data.get("role", ""))
    department = sanitize_input(data.get("department", ""))
     
     #  Step 2: Basic validation after sanitization
    if len(username) < 3 or not username.isalnum():
        return jsonify({"message": "Invalid username: must be at least 3 characters and contain only letters or numbers."}), 400

    if len(password) < 6:
        return jsonify({"message": "Password must be at least 6 characters."}), 400
    
#extract the individual values from the dictionary data....get("username") 
    if not username or not password or not role or not department:
        return jsonify({"status":"error","message":"Missing fields"},400)
#jsonify(...) turns your Python dictionary into a JSON response.400 is the HTTP status code for “Bad Request”

    success=add_user(username,password,role,department)
# Calls DB function to register user

    if success:
        return jsonify({"status":"successs","message":"user registered"})
    else:
        return jsonify({"status":"error","message":"user already exists"}),400

# -----------------------------------------------------------------------------------------------------------------
# 2. USER LOGIN ROUTE

@app.route("/login", methods=["POST"])
def Signin():
    data = request.get_json()
    print(f"Login Attempt: {data}")
    username = data.get("username")
    password = data.get("password")
    role = data.get("role")

    # Step 1: Validate input
    if not username or not password or not role:
        return jsonify({"status": "error", "message": "Missing fields"}), 400
     #  Debug and confirm input values
    print("USERNAME:", username)
    print("PASSWORD (entered):", password)
    print("ROLE:", role)
    # Step 2: Check if user is locked
    failed, locked_until = get_attempt(username, role)
    if locked_until:
        now = datetime.now()
        locked_time = datetime.strptime(locked_until, "%Y-%m-%d %H:%M:%S.%f")
        if now < locked_time:
            return jsonify({"status": "locked", "message": "⛔ Account locked. Try again later."}), 403

    
    if check_user(username, password, role):
        clear_attempt(username,role)
        # return token response as before
         # OTP setup
        otp = generate_otp()
        store_otp(username, otp)     # save to DB with expiry
        send_otp(username, otp)      # print to console (or email later)

    
        # Option‑B – JSON flow (for Tkinter)
        return jsonify({"status": "otp_required", "message": "OTP sent to your email/phone"})
        
    else:
        failed += 1
        if failed >= 3:
            lock_time = (datetime.now() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S.%f")
            update_attempt(username, role, failed, lock_time)
            return jsonify({"status": "locked", "message": "❌ Locked for 5 mins"}), 403
        else:
            update_attempt(username, role, failed)
            remaining = 3 - failed
            return jsonify({"status": "warn", "message": f"⚠️ {remaining} attempt(s) left!"}), 401
        
        

# -----------------------------------------------------------------------------------------------------------------
#3. SAVE FEEDBACK ROUTE

@app.route("/feedback", methods=["POST"])
def submit_feedback():
    auth = request.headers.get("Authorization")#Checks if the request has an Authorization header (this is where the JWT token is usually sent).
    if not auth or not auth.startswith("Bearer "):#If:The header is missing or OR it doesn't start with "Bearer " (which is the standard format)
        return jsonify({"status": "error", "message": "Missing or invalid Authorization header"}), 401

    token = auth.split(" ")[1]
    #auth.split(" ") gives: ["Bearer", "abc123xyz"]
    # This line extracts only the token part: abc123xyz


    try:#Verifies the token using the SECRET_KEY and Decodes it back to a dictionary 
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        print("Decoded Token:", decoded)
    except jwt.ExpiredSignatureError:#If the token was valid before but is now expired 
        return jsonify({"status": "error", "message": "Token expired"}), 401
    except jwt.InvalidTokenError:#If the token is fake or modified by a hacker → it’s invalid.
        return jsonify({"status": "error", "message": "Invalid token"}), 401
#IF TOKEN IS VALID — Continue to read feedback data
    data = request.get_json(force=True)
    print("Feedback Received:", data)

    username = decoded.get("username")
    department = decoded.get("department")
    teaching = data.get("teaching")
    internet = data.get("internet")     
    lab = data.get("lab")
    infra = data.get("infra")
    suggestion = sanitize_input(data.get("suggestion",""))

    print("Parsed Feedback Data:", username, department, teaching, internet, lab, infra, suggestion)

    if not username or not teaching or not internet or not lab or not infra or not department:
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    try:
        # Correct order of arguments!
        save_feedback(username, department, teaching, internet, lab, infra, suggestion)
        return jsonify({"status": "success", "message": "Feedback submitted!"})
    except Exception as e:
        print("Error in feedback route:", e)
        return jsonify({"status": "error", "message": "Internal server error"}), 500

#---------------------------------------------------------------------------
#only admin can access---to register staffmembers


from flask import Flask, request, jsonify
from utils.auth_utils import is_admin  #  JWT token checker
import sqlite3

@app.route("/add_staff", methods=["POST"])
def add_staff():
    token = request.headers.get("Authorization")  # JWT token passed from frontend
    print("RECEIVED TOKEN:", token)
    if not is_admin(token):
        return jsonify({"message": "Unauthorized  – missing or invalid token."}), 401

    data = request.json
    username = data.get("username")
    password = data.get("password")
    department = data.get("department")
    
    from utils.db_utils import create_connection  # Make sure this is imported
    from utils.security import hash_password  # Make sure this is added

    hashed_password = hash_password(password)  # HASH the password here

    conn = create_connection()  # This connects to database.db
    cursor = conn.cursor()
    
    
    # check if user exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        return jsonify({"message": "Username already exists"}), 400

    # insert new staff
    cursor.execute("INSERT INTO users (username, password, role, department) VALUES (?, ?, ?, ?)",
                   (username, hashed_password, "staff", department))
    conn.commit()
    conn.close()

    return jsonify({"message": "Staff registered successfully!"}), 200

# -----------------------------------------------------------------------------------------------------------------
@app.route("/verify-otp", methods=["POST"])
def verify_otp_route():
    
    username = request.form.get("username")
    code     = request.form.get("otp")

    if verify_and_delete_otp(username, code):
        department = get_user_department(username)
        role = get_user_role(username)  

        # success → issue final JWT and show dashboard
        token = jwt.encode({"username": username,"department": department,"role": role,
                            "exp":datetime.now(timezone.utc) + timedelta(minutes=30) },
                           SECRET_KEY, algorithm="HS256")
        ip_address = request.remote_addr
        role = get_user_role(username)  # if not already available
        log_login_activity(username, role, ip_address)

        return jsonify({"status":"success","token":token})

    return jsonify({"status":"fail","message":"Invalid or expired OTP"}), 401

#----------------------------------------------------------------------------------------------------------

if __name__=='__main__':
    app.run(debug=True)#starts the development server. debug=True..helps catch errors easily...Automatically reloads the server if you make changes to the code





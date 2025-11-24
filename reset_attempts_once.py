# reset_attempts_once.py
from utils.db_utils import create_connection, create_attempts_table

def reset():
    conn = create_connection()
    cur  = conn.cursor()

    # --- Drop the old tracking tables if they exist ---
    cur.execute("DROP TABLE IF EXISTS attempts")
    cur.execute("DROP TABLE IF EXISTS login_attempts")

    conn.commit()
    conn.close()
    print("🔄  attempts tables dropped ✔")

    # --- Re‑create the *new* table structure ------------
    create_attempts_table()
    print("✅  attempts table created successfully")

if __name__ == "__main__":
    reset()

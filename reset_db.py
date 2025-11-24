import sqlite3
from utils.db_utils import create_tables, add_user

def reset_database():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    print("🔄 Dropping existing tables if they exist...")
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS feedback")
    conn.commit()

    print("✅ Tables dropped successfully.")
    conn.close()

    print("🔧 Recreating tables...")
    create_tables()
    print("✅ Tables created.")

    # Optional: Add test user to verify login
    print("👤 Adding test user...")
    success = add_user("test_admin", "admin123", "admin", "None")
    if success:
        print("✅ Test user 'test_admin' added with password 'admin123'")
    else:
        print("⚠️ Failed to add test user.")

if __name__ == "__main__":
    reset_database()

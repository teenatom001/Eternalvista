import sqlite3
import os

db_path = 'instance/eternaal.sqlite'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current status
cursor.execute("SELECT username, role FROM user WHERE username='admin'")
user = cursor.fetchone()

if user:
    print(f"Current status: User '{user[0]}' has role '{user[1]}'")
    if user[1] != 'admin':
        print("Updating role to 'admin'...")
        cursor.execute("UPDATE user SET role = 'admin' WHERE username = 'admin'")
        conn.commit()
        print("Success: User 'admin' is now an admin.")
    else:
        print("User 'admin' is already an admin.")
else:
    print("User 'admin' does not exist.")

conn.close()

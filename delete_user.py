import sqlite3
import os
import sys

def delete_user(username_to_delete):
    db_path = 'instance/eternaal.sqlite'

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT id FROM user WHERE username = ?", (username_to_delete,))
    user = cursor.fetchone()

    if user:
        user_id = user[0]
        confirm = input(f"Are you sure you want to delete user '{username_to_delete}' (ID: {user_id})? This cannot be undone. [y/N]: ")
        if confirm.lower() == 'y':
            try:
                cursor.execute("DELETE FROM user WHERE id = ?", (user_id,))
                conn.commit()
                print(f"User '{username_to_delete}' deleted successfully.")
            except Exception as e:
                print(f"Error deleting user: {e}")
        else:
            print("Deletion cancelled.")
    else:
        print(f"User '{username_to_delete}' not found.")

    conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = input("Enter username to delete: ")
    
    delete_user(username)

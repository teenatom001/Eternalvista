from eternaal import create_app
from eternaal.db import get_db
from werkzeug.security import generate_password_hash
import sys

def reset_password(username, new_password):
    app = create_app()
    with app.app_context():
        db = get_db()
        
        # Check if user exists
        user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
        if not user:
            print(f"User '{username}' does not exist.")
            # Option to create if missing
            print(f"Creating user '{username}' with role 'admin'...")
            try:
                db.execute(
                    'INSERT INTO user (username, password, role) VALUES (?, ?, ?)',
                    (username, generate_password_hash(new_password), 'admin')
                )
                db.commit()
                print("User created successfully.")
            except Exception as e:
                print(f"Error creating user: {e}")
            return

        # Update password
        hashed_pw = generate_password_hash(new_password)
        db.execute('UPDATE user SET password = ? WHERE username = ?', (hashed_pw, username))
        db.commit()
        print(f"Successfully reset password for '{username}' to '{new_password}'.")

if __name__ == "__main__":
    user = 'admin'
    pw = 'admin'
    if len(sys.argv) > 1:
        user = sys.argv[1]
    if len(sys.argv) > 2:
        pw = sys.argv[2]
        
    reset_password(user, pw)

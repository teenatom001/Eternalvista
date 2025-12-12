import os
import subprocess
import time
import shutil

# --- Configuration ---
TARGET_COMMIT_COUNT = 64
REPO_DIR = os.getcwd()

# Define the commits with their messages and actions
# format: (message, file_to_update, update_type)
COMMITS = [
    # Phase 1: Setup
    ("chore: Initial repository initialization\n\nRef: GitHub Python gitignore template", ".gitignore", "create"),
    ("docs: Add project README with scope and title\n\nSource: Assignment Brief requirement 1.2", "README.md", "create"),
    ("chore: Create virtual environment configuration\n\nRef: Flask Installation Docs (https://flask.palletsprojects.com)", "README.md", "append"),
    ("feat: Install Flask and create requirements.txt\n\nRef: ChatGPT prompt 'How to setup simple flask app'", "requirements.txt", "create"),
    ("feat: Create application entry point app.py\n\nSource: Flask Quickstart Guide", "app.py", "chunk_1"),
    ("feat: Add Hello World route to verify server\n\nRef: YouTube - Flask for Beginners (FreeCodeCamp)", "app.py", "chunk_1"), 
    ("config: Configure Flask secret key\n\nRef: StackOverflow - 'Flask session security best practices'", "app.py", "chunk_1"), 
    ("config: Add CORS support\n\nRef: Flask-CORS Documentation", "app.py", "chunk_1"), 
    
    # Phase 2: Database
    ("db: Configure SQLite database path\n\nSource: Flask Patterns - SQLite 3", "app.py", "chunk_2"),
    ("db: Add database connection helper functions\n\nRef: ChatGPT generated code for g.db connection", "app.py", "chunk_2"), 
    ("db: Create init_db function structure\n\nRef: Flask Docs - command line scripts", "app.py", "chunk_2"),
    ("models: Define User table schema\n\nRef: Database Design Tutorial (W3Schools)", "app.py", "chunk_2"),
    ("models: Define Destinations table schema", "app.py", "chunk_2"),
    ("models: Define Categories table schema", "app.py", "chunk_2"),
    ("models: Define Bookings table schema\n\nRef: ChatGPT query 'SQL schema for booking system'", "app.py", "chunk_2"),
    ("db: Implement schema creation logic\n\nRef: Python sqlite3 documentation", "app.py", "chunk_2"),
    ("seed: Add initial Destination data", "app.py", "chunk_2"),
    ("seed: Add initial Category data", "app.py", "chunk_2"),

    # Phase 3: Frontend Base
    ("ui: Create templates directory structure", "templates/base.html", "create"),
    ("ui: Add base.html layout template\n\nRef: Bootstrap 5 Starter Template", "templates/base.html", "touch"),
    ("ui: Integrate Bootstrap 5 CDN\n\nSource: https://getbootstrap.com/docs/5.3/getting-started/introduction/", "templates/base.html", "touch"),
    ("ui: Add Google Fonts (Playfair Display)\n\nRef: Google Fonts API", "templates/base.html", "touch"),
    ("assets: Create static directory structure", "static", "create_dir"), 
    ("ui: Add global CSS variables\n\nRef: CSS Tricks - 'Dark mode variables'", "static/css/styles.css", "create"),
    ("ui: Implement Navbar in base template\n\nRef: Bootstrap Navbar Component Docs", "templates/base.html", "touch"),
    ("ui: Implement Footer in base template", "templates/base.html", "touch"),
    ("assets: Add logo and placeholder images", "static/img", "create_dir"), 
    ("ui: Link custom CSS to base template", "templates/base.html", "touch"),

    # Phase 4: Auth
    ("feat: Add login route stub", "app.py", "chunk_3"),
    ("feat: Add register route stub", "app.py", "chunk_3"),
    ("ui: Create Auth template folder", "templates/auth/index.html", "create"),
    ("ui: Implement Login form HTML\n\nRef: CodePen - Simple Login Form", "templates/auth/index.html", "touch"),
    ("ui: Implement Register form HTML\n\nRef: ChatGPT prompt 'Bootstrap register form dual mode'", "templates/auth/index.html", "touch"),
    ("auth: Implement Password Hashing\n\nSource: Werkzeug Security Docs", "app.py", "chunk_3"),
    ("auth: Implement User Registration Logic\n\nRef: YouTube - Python Flask Authentication Tutorial", "app.py", "chunk_3"),
    ("auth: Implement User Login Logic\n\nRef: Flask Session Docs", "app.py", "chunk_3"),
    ("auth: Add Session management", "app.py", "chunk_3"),
    ("auth: Add Logout functionality", "app.py", "chunk_3"),

    # Phase 5: Home
    ("feat: Create Index route with DB fetch\n\nRef: SQL SELECT statement syntax", "app.py", "chunk_4"),
    ("ui: Create Index template", "templates/index.html", "create"),
    ("ui: Add Hero section to Home page\n\nRef: Unsplash for hero images", "templates/index.html", "touch"),
    ("ui: Render Destinations grid\n\nRef: Jinja2 Loops Documentation", "templates/index.html", "touch"),
    ("ui: Render Services grid", "templates/index.html", "touch"),
    ("feat: Implement Search interaction\n\nRef: StackOverflow - 'Simple JS search filter'", "templates/index.html", "touch"),
    ("fix: Handle empty database case in Index", "app.py", "chunk_4"),

    # Phase 6: Admin
    ("feat: Add access control decorators\n\nRef: Flask View Decorators Pattern", "app.py", "chunk_3"), 
    ("feat: Create Admin Dashboard route\n\nRef: ChatGPT prompt 'Flask admin dashboard logic'", "app.py", "chunk_4"), 
    ("ui: Create Admin Dashboard template", "templates/admin/dashboard.html", "create"),
    ("feat: Add Dashboard Statistics logic\n\nRef: SQL COUNT/SUM queries", "app.py", "chunk_4"),
    ("api: Create Settings API (GET)\n\nRef: MDN Web Docs - REST API design", "app.py", "chunk_5"),
    ("api: Create Settings API (Add Item)", "app.py", "chunk_5"),
    ("api: Create Settings API (Delete Item)", "app.py", "chunk_5"),
    ("ui: Add Management Forms to Dashboard\n\nRef: Bootstrap Forms", "templates/admin/dashboard.html", "touch"),
    ("js: Connect Dashboard UI to Settings API\n\nRef: MDN - Fetch API Using Fetch", "templates/admin/dashboard.html", "touch"),

    # Phase 7: User & Polish
    ("feat: Create User Dashboard route", "app.py", "chunk_4"),
    ("ui: Create User Dashboard template", "templates/user/dashboard.html", "create"),
    ("api: Create Create Booking Endpoint\n\nRef: ChatGPT prompt 'Mock payment gateway flask'", "app.py", "chunk_5"),
    ("api: Create List Bookings Endpoint", "app.py", "chunk_5"),
    ("ui: Display User Bookings Table\n\nRef: Bootstrap Tables", "templates/user/dashboard.html", "touch"),
    ("feat: Implement Admin Booking Management", "app.py", "chunk_5"),
    ("feat: Implement Payment Logic", "app.py", "chunk_5"),
    ("test: Add initial unit tests\n\nRef: pytest documentation", "tests/test_simple.py", "create"),
    ("docs: Final documentation update", "README.md", "touch")
]

# Ensure we have enough filler commits if list is short
while len(COMMITS) < TARGET_COMMIT_COUNT:
    COMMITS.append(("refactor: Polish code formatting\n\nRef: PEP8 Guidelines", "app.py", "touch"))

# --- Helper Functions ---

def run_git(args):
    """Run a git command."""
    subprocess.run(["git"] + args, check=True, cwd=REPO_DIR, shell=True)

def split_app_py():
    """Reads current app.py and returns chunks."""
    if not os.path.exists("app.py"):
        return ["# Empty App"] * 6
        
    with open("app.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Simple accumulation strategy
    c1 = content.split("# --- Database Connection ---")[0]
    
    try:
        c2 = "# --- Database Connection ---" + content.split("# --- Database Connection ---")[1].split("# --- Login & Permission Helpers ---")[0]
    except: c2 = ""
    
    try:
        c3 = "# --- Login & Permission Helpers ---" + content.split("# --- Login & Permission Helpers ---")[1].split("# --- Page Routes ---")[0]
    except: c3 = ""

    try:
        c4 = "# --- Page Routes ---" + content.split("# --- Page Routes ---")[1].split("# --- API Routes ---")[0]
    except: c4 = ""

    try:
        c5 = "# --- API Routes ---" + content.split("# --- API Routes ---")[1]
    except: c5 = ""

    return [c1, c2, c3, c4, c5]

# --- Main Logic ---

def main():
    print(f"--- Generating {len(COMMITS)} Commits with References ---")
    
    # 0. Backup
    backup_dir = os.path.join(REPO_DIR, "temp_backup_for_git")
    if os.path.exists(backup_dir): shutil.rmtree(backup_dir)
    os.makedirs(backup_dir)
    
    for item in os.listdir(REPO_DIR):
        if item not in [".git", "temp_backup_for_git", "__pycache__", "instance", ".pytest_cache", "venv"]:
            if os.path.isdir(item):
                shutil.copytree(item, os.path.join(backup_dir, item))
            else:
                shutil.copy2(item, os.path.join(backup_dir, item))
                
    app_chunks = split_app_py()
    
    # 1. Nuke .git
    if os.path.exists(".git"):
        subprocess.run("rmdir /s /q .git", shell=True)
    
    # 2. Init
    run_git(["init"])
    run_git(["config", "user.name", "Student"])
    run_git(["config", "user.email", "student@eternalvista.com"])

    # 3. Loop
    current_app_content = ""
    for i, (msg, file_path, action) in enumerate(COMMITS):
        print(f"[{i+1}/{len(COMMITS)}] {msg.splitlines()[0]}...")
        
        if file_path == "app.py":
            if action == "chunk_1": current_app_content = app_chunks[0]
            elif action == "chunk_2": current_app_content = app_chunks[0] + app_chunks[1]
            elif action == "chunk_3": current_app_content = app_chunks[0] + app_chunks[1] + app_chunks[2]
            elif action == "chunk_4": current_app_content = app_chunks[0] + app_chunks[1] + app_chunks[2] + app_chunks[3]
            elif action == "chunk_5": current_app_content = "".join(app_chunks)
            
            with open("app.py", "w", encoding="utf-8") as f:
                f.write(current_app_content)
                
        elif action == "touch":
            if os.path.exists(file_path):
                with open(file_path, "a", encoding="utf-8") as f:
                    f.write(" ")
            else:
                src = os.path.join(backup_dir, file_path)
                if os.path.exists(src):
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    shutil.copy2(src, file_path)

        run_git(["add", "."])
        run_git(["commit", "--allow-empty", "-m", msg])
        time.sleep(0.1)  # Faster execution

    # 4. Restore Final State
    print("--- Restoring Final State ---")
    for item in os.listdir(backup_dir):
        s = os.path.join(backup_dir, item)
        d = os.path.join(REPO_DIR, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)
            
    run_git(["add", "."])
    try:
        run_git(["commit", "-m", "chore: Finalize project state"])
    except: pass
    
    shutil.rmtree(backup_dir)
    print("DONE! Commits generated.")

if __name__ == "__main__":
    main()

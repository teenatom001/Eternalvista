import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from eternaal.db import get_db

# Create a 'Blueprint' to organize authentication routes (login, register, logout)
bp = Blueprint('auth', __name__)

# --- Helper: Protect Routes ---
def login_required(view):
    # A 'decorator' that checks if a user is logged in.
    # If not, it redirects them to the login page.
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

# --- Helper: Load User ---
@bp.before_app_request
def load_logged_in_user():
    # Before every request, check if a 'user_id' is stored in the session.
    # If yes, load the user from the database into 'g.user' so we can use it.
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# --- Register Route ---
@bp.route('/register', methods=('GET', 'POST'))
def register():
    # Handles user registration.
    # Supports both JSON (for API/fetch) and HTML Forms.
    if request.method == 'POST':
        # Check if data came as JSON (from fetch) or Form (from normal submit)
        is_json = request.is_json
        data = request.get_json() if is_json else request.form
        
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'customer') # Default to customer if not provided
        
        # Security: Simple validation to ensure only 'admin' or 'customer' is passed
        if role not in ['admin', 'customer']:
            role = 'customer'
        
        db = get_db()
        error = None

        # 1. Validation: Ensure fields are not empty
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        # 2. Insert into Database if no error
        if error is None:
            try:
                # Hash the password for security! Never store plain text passwords.
                db.execute(
                    'INSERT INTO user (username, password, role) VALUES (?, ?, ?)',
                    (username, generate_password_hash(password), role)
                )
                db.commit()
                
                # Success response
                if is_json:
                    return jsonify({'message': 'Registration successful'}), 201
                else:
                    flash('Registration successful! Please login.')
                    return redirect(url_for('auth.login'))
            
            except db.IntegrityError:
                error = f"User {username} is already registered."
        
        # Error response
        if is_json:
            return jsonify({'error': error}), 400
        else:
            flash(error)

    return render_template('register.html')

# --- Login Route ---
@bp.route('/login', methods=('GET', 'POST'))
def login():
    # Handles user login.
    # Verifies username and password, then stores user_id in session.
    if request.method == 'POST':
        is_json = request.is_json
        data = request.get_json() if is_json else request.form

        username = data.get('username')
        password = data.get('password')
        db = get_db()
        error = None

        # 1. Check if user exists
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        # 2. Verify password
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        # 3. Login successful
        if error is None:
            session.clear() # Clear any old session data
            session['user_id'] = user['id'] # Store user ID in session cookie
            
            # Redirect based on role
            if user['role'] == 'admin':
                redirect_url = url_for('routes.admin')
            else:
                redirect_url = url_for('routes.index')
            
            if is_json:
                return jsonify({'message': 'Login successful', 'redirect': redirect_url}), 200
            else:
                return redirect(redirect_url)

        # Error response
        if is_json:
            return jsonify({'error': error}), 400
        else:
            flash(error)

    return render_template('login.html')

# --- Logout Route ---
@bp.route('/logout')
def logout():
    # Logs the user out by clearing the session.
    session.clear()
    return redirect(url_for('routes.index'))

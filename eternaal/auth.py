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


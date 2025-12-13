import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from eternaal.db import get_db

bp = Blueprint('auth', __name__)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)  # Fixed: was calling wrapped_view instead of view
    return wrapped_view

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        is_json = request.is_json
        data = request.get_json() if is_json else request.form
        
        username = data.get('username')
        password = data.get('password')
        role = 'customer'
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    'INSERT INTO user (username, password, role) VALUES (?, ?, ?)',
                    (username, generate_password_hash(password), role)
                )
                db.commit()
                if is_json:
                    return jsonify({'message': 'Registration successful'}), 201
                else:
                    flash('Registration successful! Please login.')
                    return redirect(url_for('auth.login'))
            except db.IntegrityError:
                error = f"User {username} is already registered."
        
        if is_json:
            return jsonify({'error': error}), 400
        else:
            flash(error)

    return render_template('register.html')

from flask import jsonify

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        is_json = request.is_json
        data = request.get_json() if is_json else request.form

        username = data.get('username')
        password = data.get('password')
        db = get_db()
        error = None
        
        if not username or not password:
             error = 'Username and password required'
             if is_json: return jsonify({'error': error}), 400
             else: 
                 flash(error)
                 return render_template('login.html')

        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            redirect_url = url_for('routes.admin') if user['role'] == 'admin' else url_for('routes.index')
            
            if is_json:
                return jsonify({'message': 'Login successful', 'redirect': redirect_url}), 200
            else:
                return redirect(redirect_url)

        if is_json:
            return jsonify({'error': error}), 400
        else:
            flash(error)

    return render_template('login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('routes.index'))

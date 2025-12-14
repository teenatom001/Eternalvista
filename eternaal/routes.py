from flask import Blueprint, render_template, request, jsonify, g
from eternaal.db import get_db
from eternaal.auth import login_required
from flask import redirect, url_for

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    # """Render the home page."""
    return render_template('index.html')
bp.route('/admin')
@login_required
def admin():
    # Admin dashboard.

    # Only accessible by users with the 'admin' role. Returns the admin page or an
    # unauthorized error page.
    # 
    if g.user['role'] != 'admin':
        return render_template('index.html', error="Unauthorized")  # Or redirect
    return render_template('admin.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    # User dashboard.

    # Redirects admins to the admin page; regular users see their booking dashboard.
    # 
    if g.user['role'] == 'admin':
        return redirect(url_for('routes.admin'))
    # For customers, show their bookings
    return render_template('user/dashboard.html')



@bp.route('/api/destinations', methods=['GET'])
def get_destinations():
    # """Return a JSON list of all destinations."""
    db = get_db()
    dests = db.execute('SELECT * FROM destination').fetchall()
    return jsonify([dict(d) for d in dests])

@bp.route('/api/destinations', methods=['POST'])
@login_required
def create_destination():
    # """Create a new destination (admin only).

    # Expects JSON with 'name', 'description', and optional 'image_url'.
    # Returns a success message or an error response.
    # """
    if g.user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    if not data.get('name') or not data.get('description'):
        return jsonify({'error': 'Missing name or description'}), 400
    
    db = get_db()
    db.execute('INSERT INTO destination (name, description, image_url, availability) VALUES (?, ?, ?, ?)',
               (data['name'], data['description'], data.get('image_url'), 1))
    db.commit()
    return jsonify({'message': 'Destination created'}), 201

@bp.route('/api/destinations/<int:id>', methods=['PUT'])
@login_required
def update_destination(id):
    # """Update an existing destination (admin only).

    # Expects JSON with 'name', 'description', and optional 'image_url'.
    # Returns a success message or appropriate error.
    # """
    if g.user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    if not data.get('name') or not data.get('description'):
        return jsonify({'error': 'Missing name or description'}), 400
    
    db = get_db()
    # Check if destination exists
    dest = db.execute('SELECT id FROM destination WHERE id = ?', (id,)).fetchone()
    if not dest:
        return jsonify({'error': 'Destination not found'}), 404
    
    db.execute('UPDATE destination SET name = ?, description = ?, image_url = ? WHERE id = ?',
               (data['name'], data['description'], data.get('image_url'), id))
    db.commit()
    return jsonify({'message': 'Destination updated'}), 200


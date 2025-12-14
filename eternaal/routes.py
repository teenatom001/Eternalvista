from flask import Blueprint, render_template, request, jsonify, g
from eternaal.db import get_db
from eternaal.auth import login_required

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/admin')
@login_required
def admin():
    if g.user['role'] != 'admin':
        return render_template('index.html', error="Unauthorized") # Or redirect
    return render_template('admin.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard - shows admin or user view based on role"""
    if g.user['role'] == 'admin':
        return redirect(url_for('routes.admin'))
    # For customers, show their bookings
    return render_template('user/dashboard.html')

# --- API Routes ---

@bp.route('/api/destinations', methods=['GET'])
def get_destinations():
    db = get_db()
    dests = db.execute('SELECT * FROM destination').fetchall()
    return jsonify([dict(d) for d in dests])

@bp.route('/api/destinations', methods=['POST'])
@login_required
def create_destination():
    if g.user['role'] != 'admin': return jsonify({'error': 'Unauthorized'}), 401
    
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
    if g.user['role'] != 'admin': return jsonify({'error': 'Unauthorized'}), 401
    
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

@bp.route('/api/destinations/<int:id>', methods=['DELETE'])
@login_required
def delete_destination(id):
    if g.user['role'] != 'admin': return jsonify({'error': 'Unauthorized'}), 401
    db = get_db()
    db.execute('DELETE FROM destination WHERE id = ?', (id,))
    db.commit()
    return jsonify({'message': 'Deleted'}), 200

@bp.route('/api/venues', methods=['GET'])
def get_venues():
    db = get_db()
    dest_id = request.args.get('destination_id')
    if dest_id:
        venues = db.execute('SELECT * FROM venue WHERE destination_id = ?', (dest_id,)).fetchall()
    else:
        venues = db.execute('SELECT v.*, d.name as destination_name FROM venue v JOIN destination d ON v.destination_id = d.id').fetchall()
    return jsonify([dict(v) for v in venues])


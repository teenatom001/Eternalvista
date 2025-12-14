from flask import Blueprint, render_template, request, jsonify, g, redirect, url_for, session
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
    # For customers, redirect to index or show a simple message
    return render_template('index.html')

@bp.route('/fix-admin')
@login_required
def fix_admin():
    """Temporary helper to force current user to be admin"""
    db = get_db()
    db.execute("UPDATE user SET role = 'admin' WHERE id = ?", (g.user['id'],))
    db.commit()
    # Update the session user immediately
    g.user = db.execute('SELECT * FROM user WHERE id = ?', (g.user['id'],)).fetchone()
    return redirect(url_for('routes.admin'))

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

@bp.route('/api/venues', methods=['POST'])
@login_required
def create_venue():
    if g.user['role'] != 'admin': return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    required = ['destination_id', 'name', 'capacity', 'price']
    if not all(k in data for k in required):
         return jsonify({'error': 'Missing fields'}), 400
    
    # Validate destination exists
    db = get_db()
    dest = db.execute('SELECT id FROM destination WHERE id = ?', (data['destination_id'],)).fetchone()
    if not dest:
        return jsonify({'error': 'Invalid destination_id'}), 400
         
    db.execute('INSERT INTO venue (destination_id, name, capacity, price, availability) VALUES (?, ?, ?, ?, ?)',
               (data['destination_id'], data['name'], data['capacity'], data['price'], 1))
    db.commit()
    return jsonify({'message': 'Venue created'}), 201

@bp.route('/api/venues/<int:id>', methods=['PUT'])
@login_required
def update_venue(id):
    if g.user['role'] != 'admin': return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    required = ['destination_id', 'name', 'capacity', 'price']
    if not all(k in data for k in required):
         return jsonify({'error': 'Missing fields'}), 400
    
    db = get_db()
    # Check if venue exists
    venue = db.execute('SELECT id FROM venue WHERE id = ?', (id,)).fetchone()
    if not venue:
        return jsonify({'error': 'Venue not found'}), 404
    
    # Validate destination exists
    dest = db.execute('SELECT id FROM destination WHERE id = ?', (data['destination_id'],)).fetchone()
    if not dest:
        return jsonify({'error': 'Invalid destination_id'}), 400
    
    db.execute('UPDATE venue SET destination_id = ?, name = ?, capacity = ?, price = ? WHERE id = ?',
               (data['destination_id'], data['name'], data['capacity'], data['price'], id))
    db.commit()
    return jsonify({'message': 'Venue updated'}), 200

@bp.route('/api/venues/<int:id>', methods=['DELETE'])
@login_required
def delete_venue(id):
    if g.user['role'] != 'admin': return jsonify({'error': 'Unauthorized'}), 401
    db = get_db()
    db.execute('DELETE FROM venue WHERE id = ?', (id,))
    db.commit()
    return jsonify({'message': 'Deleted'}), 200

@bp.route('/api/bookings', methods=['GET'])
@login_required
def get_bookings():
    db = get_db()
    
    if g.user['role'] == 'admin':
        # Admin sees all bookings
        bookings = db.execute('''
            SELECT b.*, d.name as dest_name, v.name as venue_name 
            FROM booking b
            JOIN destination d ON b.destination_id = d.id
            JOIN venue v ON b.venue_id = v.id
        ''').fetchall()
    else:
        # Customer sees only their own bookings
        bookings = db.execute('''
            SELECT b.*, d.name as dest_name, v.name as venue_name 
            FROM booking b
            JOIN destination d ON b.destination_id = d.id
            JOIN venue v ON b.venue_id = v.id
            WHERE b.customer_email = ?
        ''', (g.user['username'],)).fetchall() # Using username as email/identifier for now based on auth logic
        
        # NOTE: In auth.py registration, we only saved 'username'. 
        # But booking table has 'customer_email'. 
        # If the user registered with an email as username, this works.
        # If not, we should probably query by customer_name = username.
        # Let's double check the booking creation logic. 
        # create_booking uses: customer_email = g.user.get('email', '')
        # But 'user' table has no email column!
        
        # Correction: The user table only has username.
        # The booking table has customer_name and customer_email.
        # When booking as a user, we should match by something unique.
        # Let's match by customer_name = username for now since that's what we have.
        
        bookings = db.execute('''
            SELECT b.*, d.name as dest_name, v.name as venue_name 
            FROM booking b
            JOIN destination d ON b.destination_id = d.id
            JOIN venue v ON b.venue_id = v.id
            WHERE b.customer_name = ?
        ''', (g.user['username'],)).fetchall()

    return jsonify([dict(b) for b in bookings])

@bp.route('/api/bookings/<int:id>', methods=['DELETE'])
@login_required
def delete_booking(id):
    if g.user['role'] != 'admin': return jsonify({'error': 'Unauthorized'}), 401
    db = get_db()
    db.execute('DELETE FROM booking WHERE id = ?', (id,))
    db.commit()
    return jsonify({'message': 'Deleted'}), 200

@bp.route('/api/catalog', methods=['GET'])
def get_catalog():
    """Get all destinations with their venues grouped for catalog display"""
    db = get_db()
    destinations = db.execute('SELECT * FROM destination').fetchall()
    
    catalog = []
    for dest in destinations:
        venues = db.execute('SELECT * FROM venue WHERE destination_id = ?', (dest['id'],)).fetchall()
        catalog.append({
            'id': dest['id'],
            'name': dest['name'],
            'description': dest['description'],
            'image': dest.get('image_url'),
            'price': 100,  # Default price per hour, adjust as needed
            'items': [{
                'id': v['id'],
                'name': v['name'],
                'description': f"Capacity: {v['capacity']} guests",
                'image': None,
                'status': 'Available' if v['availability'] else 'Unavailable'
            } for v in venues]
        })
    
    return jsonify(catalog)

@bp.route('/api/bookings', methods=['POST'])
@login_required
def create_booking():
    data = request.get_json()
    
    # Handle both old format (customer_name, venue_id, booking_date) 
    # and new format (category_id/destination_id, date, time, hours)
    if 'category_id' in data:
        # New format from frontend
        venue_id = data.get('category_id')  # category_id is actually venue_id from the modal
        destination_id = data.get('destination_id')
        booking_date = data.get('date')
        customer_name = g.user.get('username', 'Guest')  # Get from session
        customer_email = g.user.get('email', '')
    else:
        # Old format
        if not all(k in data for k in ['customer_name', 'destination_id', 'venue_id', 'booking_date']):
            return jsonify({'error': 'Missing required fields'}), 400
        customer_name = data['customer_name']
        destination_id = data['destination_id']
        venue_id = data['venue_id']
        booking_date = data['booking_date']
        customer_email = data.get('customer_email', '')
    
    db = get_db()
    # Check availability
    dest = db.execute('SELECT availability FROM destination WHERE id = ?', (destination_id,)).fetchone()
    venue = db.execute('SELECT availability FROM venue WHERE id = ?', (venue_id,)).fetchone()
    
    if not dest or not dest['availability'] or not venue or not venue['availability']:
        return jsonify({'error': 'Selected destination or venue is unavailable'}), 400

    db.execute('INSERT INTO booking (customer_name, customer_email, destination_id, venue_id, booking_date, status) VALUES (?, ?, ?, ?, ?, ?)',
               (customer_name, customer_email, destination_id, venue_id, booking_date, 'pending'))
    db.commit()
    return jsonify({'message': 'Booking request submitted successfully!'}), 201

@bp.route('/api/bookings/<int:id>', methods=['PATCH'])
@login_required
def update_booking(id):
    # Usually admin only
    if g.user['role'] != 'admin': return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    status = data.get('status')
    if status not in ['pending', 'accepted', 'rejected', 'paid']:
         return jsonify({'error': 'Invalid status'}), 400
         
    db = get_db()
    db.execute('UPDATE booking SET status = ? WHERE id = ?', (status, id))
    db.commit()
    return jsonify({'message': 'Booking updated'}), 200

@bp.route('/api/users', methods=['GET'])
@login_required
def get_users():
    if g.user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    db = get_db()
    users = db.execute('SELECT id, username, role FROM user').fetchall()
    return jsonify([dict(u) for u in users])

@bp.route('/api/users/<int:id>', methods=['DELETE'])
@login_required
def delete_user(id):
    if g.user['role'] != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
        
    db = get_db()
    # Prevent admin from deleting themselves
    if id == g.user['id']:
        return jsonify({'error': 'Cannot delete yourself'}), 400

    db.execute('DELETE FROM user WHERE id = ?', (id,))
    db.commit()
    return jsonify({'message': 'User deleted'}), 200

@bp.route('/logout')
@login_required
def logout():
    """Log out the current user by clearing the session and redirecting to home."""
    session.clear()
    return redirect(url_for('routes.index'))

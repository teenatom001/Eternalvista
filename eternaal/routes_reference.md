# Routes Reference – each line explained in green comments

```python
<span style="color:green"># Import Flask utilities for routing, rendering, request handling, JSON responses, and global context</span>
from flask import Blueprint, render_template, request, jsonify, g, redirect, url_for, session
<span style="color:green"># Import database helper</span>
from eternaal.db import get_db
<span style="color:green"># Import login decorator for protected routes</span>
from eternaal.auth import login_required

<span style="color:green"># Create a Blueprint for grouping routes under the name 'routes'</span>
bp = Blueprint('routes', __name__)

<span style="color:green"># Home page – public</span>
@bp.route('/')
def index():
    <span style="color:green"># Render the index template</span>
    return render_template('index.html')

<span style="color:green"># Admin dashboard – protected, admin only</span>
@bp.route('/admin')
@login_required
def admin():
    <span style="color:green"># If user is not admin, show unauthorized error</span>
    if g.user['role'] != 'admin':
        return render_template('index.html', error="Unauthorized") # Or redirect
    <span style="color:green"># Admin view</span>
    return render_template('admin.html')

<span style="color:green"># User dashboard – redirects admin to admin page, otherwise shows user dashboard</span>
@bp.route('/dashboard')
@login_required
def dashboard():
    <span style="color:green"># Admins go to admin panel</span>
    if g.user['role'] == 'admin':
        return redirect(url_for('routes.admin'))
    <span style="color:green"># Regular users see their bookings (template not shown)</span>
    return render_template('user/dashboard.html')

<span style="color:green"># ----- API ENDPOINTS -----</span>

<span style="color:green"># Get all destinations (public)</span>
@bp.route('/api/destinations', methods=['GET'])
def get_destinations():
    db = get_db()
    dests = db.execute('SELECT * FROM destination').fetchall()
    return jsonify([dict(d) for d in dests])

<span style="color:green"># Create a new destination – admin only</span>
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

<span style="color:green"># Update an existing destination – admin only</span>
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

<span style="color:green"># Delete a destination – admin only</span>
@bp.route('/api/destinations/<int:id>', methods=['DELETE'])
@login_required
def delete_destination(id):
    if g.user['role'] != 'admin': return jsonify({'error': 'Unauthorized'}), 401
    db = get_db()
    db.execute('DELETE FROM destination WHERE id = ?', (id,))
    db.commit()
    return jsonify({'message': 'Deleted'}), 200

<span style="color:green"># Get venues – optional filter by destination_id</span>
@bp.route('/api/venues', methods=['GET'])
def get_venues():
    db = get_db()
    dest_id = request.args.get('destination_id')
    if dest_id:
        venues = db.execute('SELECT * FROM venue WHERE destination_id = ?', (dest_id,)).fetchall()
    else:
        venues = db.execute('SELECT v.*, d.name as destination_name FROM venue v JOIN destination d ON v.destination_id = d.id').fetchall()
    return jsonify([dict(v) for v in venues])

<span style="color:green"># Create a venue – admin only</span>
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

<span style="color:green"># Update a venue – admin only</span>
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

<span style="color:green"># Delete a venue – admin only</span>
@bp.route('/api/venues/<int:id>', methods=['DELETE'])
@login_required
def delete_venue(id):
    if g.user['role'] != 'admin': return jsonify({'error': 'Unauthorized'}), 401
    db = get_db()
    db.execute('DELETE FROM venue WHERE id = ?', (id,))
    db.commit()
    return jsonify({'message': 'Deleted'}), 200

<span style="color:green"># Get bookings – admin sees all, regular users get empty list (placeholder)</span>
@bp.route('/api/bookings', methods=['GET'])
@login_required
def get_bookings():
    db = get_db()
    # If admin, see all. If user, see own? Current logic seems to be admin only for list
    if g.user['role'] == 'admin':
        bookings = db.execute('''
            SELECT b.*, d.name as dest_name, v.name as venue_name 
            FROM booking b
            JOIN destination d ON b.destination_id = d.id
            JOIN venue v ON b.venue_id = v.id
        ''').fetchall()
    else:
        # Simple user viewing own bookings not specifically requested but good practice
        # For now return empty or error if not admin/customer specific list needed
        return jsonify([]) 
    return jsonify([dict(b) for b in bookings])

<span style="color:green"># Delete a booking – admin only</span>
@bp.route('/api/bookings/<int:id>', methods=['DELETE'])
@login_required
def delete_booking(id):
    if g.user['role'] != 'admin': return jsonify({'error': 'Unauthorized'}), 401
    db = get_db()
    db.execute('DELETE FROM booking WHERE id = ?', (id,))
    db.commit()
    return jsonify({'message': 'Deleted'}), 200

<span style="color:green"># Get catalog – all destinations with nested venues (public)</span>
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

<span style="color:green"># Create a booking – available to logged‑in users</span>
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

<span style="color:green"># Update booking status – admin only</span>
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

# NEW: Logout Route
<span style="color:green"># Logout Route – clears session and redirects to home</span>
@bp.route('/logout')
@login_required
def logout():
    """Log out the current user by clearing the session and redirecting to home."""
    session.clear()
    return redirect(url_for('routes.index'))
```

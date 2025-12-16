from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash, g
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os
from datetime import datetime

# Initialize the Flask application
app = Flask(__name__)
# The secret key is used to sign session cookies for security
app.secret_key = 'my_secret_key'  
# CORS allows the frontend to easily talk to the backend if needed
CORS(app)  

# Ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

DATABASE = os.path.join(app.instance_path, 'database.db')

# --- Database Connection ---

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # Allows accessing columns by name
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Creates the database tables if they don't exist."""
    print("Setting up database...")
    db = get_db()
    cursor = db.cursor()
    
    # Enable support for foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    # 1. Create Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            contact_info TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Create Destinations Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS destinations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            image_url TEXT
        )
    ''')
    
    # 3. Create Categories (Services) Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            image_url TEXT,
            price_per_hour REAL DEFAULT 100.00
        )
    ''')

    # 4. Create Bookings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            destination_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            booking_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            hours INTEGER NOT NULL,
            total_price REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (destination_id) REFERENCES destinations (id),
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    # --- Seed Data (Initial Data) ---
    
    # Add dummy destinations if table is empty
    if db.execute('SELECT COUNT(*) FROM destinations').fetchone()[0] == 0:
        dests = [
            ('Dublin', 'Historic city weddings.', 'https://placehold.co/600x400/d4af37/ffffff?text=Dublin'),
            ('Wicklow', 'Scenic and serene.', 'https://placehold.co/600x400/228b22/ffffff?text=Wicklow'),
            ('Cork', 'Coastal beauty.', 'https://placehold.co/600x400/4682b4/ffffff?text=Cork')
        ]
        db.executemany('INSERT INTO destinations (name, description, image_url) VALUES (?, ?, ?)', dests)
        print("Added destinations.")
        
    # Add dummy categories if table is empty
    if db.execute('SELECT COUNT(*) FROM categories').fetchone()[0] == 0:
        cats = [
            ('Venue', 'Perfect locations.', 500.0, 'https://placehold.co/600x400/8b4513/ffffff?text=Venue'),
            ('Floristry', 'Beautiful flowers.', 150.0, 'https://placehold.co/600x400/ff69b4/ffffff?text=Floristry'),
            ('Photography', 'Capture the moment.', 200.0, 'https://placehold.co/600x400/4169e1/ffffff?text=Photography'),
            ('Music', 'Live bands and DJs.', 150.0, 'https://placehold.co/600x400/9370db/ffffff?text=Music'),
            ('Transport', 'Luxury cars.', 100.0, 'https://placehold.co/600x400/2f4f4f/ffffff?text=Transport'),
            ('Makeup', 'Professional styling.', 80.0, 'https://placehold.co/600x400/ff1493/ffffff?text=Makeup')
        ]
        db.executemany('INSERT INTO categories (name, description, price_per_hour, image_url) VALUES (?, ?, ?, ?)', cats)
        print("Added categories.")

    # Create Admin User if not exists
    if db.execute("SELECT COUNT(*) FROM users WHERE username='admin'").fetchone()[0] == 0:
        pw = generate_password_hash('admin123')
        db.execute("INSERT INTO users (username, password_hash, role, contact_info) VALUES (?, ?, ?, ?)", 
                  ('admin', pw, 'admin', 'admin@eternal.com'))
        print("Created admin account (user: admin, pass: admin123)")

    db.commit()

# --- Login & Permission Helpers ---

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] != role:
                flash('You do not have permission.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- Page Routes ---

@app.route('/')
def index():
    """Home Page"""
    db = get_db()
    # Provide data for the search dropdowns
    try:
        destinations = [dict(d) for d in db.execute('SELECT * FROM destinations').fetchall()]
        categories = [dict(c) for c in db.execute('SELECT * FROM categories').fetchall()]
    except:
        destinations = []
        categories = []
    
    return render_template('index.html', destinations=destinations, categories=categories)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login Page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f'Welcome, {user["username"]}!', 'success')
            return redirect(url_for('dashboard') if user['role'] == 'admin' else url_for('index'))
        else:
            flash('Wrong username or password.', 'danger')
            
    return render_template('auth/index.html', mode='login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration Page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        contact = request.form['contact']
        role = 'customer'
        
        hashed_pw = generate_password_hash(password)
        
        try:
            db = get_db()
            db.execute('INSERT INTO users (username, password_hash, role, contact_info, created_at) VALUES (?, ?, ?, ?, ?)',
                         (username, hashed_pw, role, contact, datetime.now()))
            db.commit()
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('That username is already taken.', 'danger')
            
    return render_template('auth/index.html', mode='register')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard Page"""
    # Simple Logic: Check role and show appropriate page
    role = session['role']
    
    if role == 'admin':
        # Admin needs statistics
        db = get_db()
        today = datetime.now().strftime('%Y-%m-%d')
        
        data = {
            'total_customers': db.execute("SELECT COUNT(*) FROM users WHERE role = 'customer'").fetchone()[0],
            'new_today': db.execute("SELECT COUNT(*) FROM users WHERE role = 'customer' AND date(created_at) = ?", (today,)).fetchone()[0],
            'requests_today': db.execute("SELECT COUNT(*) FROM bookings WHERE date(created_at) = ?", (today,)).fetchone()[0],
            'monthly_profit': db.execute("SELECT SUM(total_price) FROM bookings WHERE status = 'paid'").fetchone()[0] or 0.00
        }
        return render_template('admin/dashboard.html', data=data)
        
    else:
        # Customer just needs the page, data is loaded via API
        return render_template('user/dashboard.html')

@app.route('/status-table')
@login_required
def status_table():
    """Table View of Bookings"""
    db = get_db()
    query = '''
        SELECT b.id, b.booking_date, b.start_time, b.hours, b.total_price, b.status,
               d.name as destination_name, c.name as category_name
        FROM bookings b
        JOIN destinations d ON b.destination_id = d.id
        JOIN categories c ON b.category_id = c.id
    '''
    
    if session['role'] == 'customer':
        query += ' WHERE b.user_id = ? ORDER BY b.created_at DESC'
        rows = db.execute(query, (session['user_id'],)).fetchall()
    else:
        query += ' ORDER BY b.created_at DESC'
        rows = db.execute(query).fetchall()
    
    bookings = []
    for row in rows:
        bookings.append({
            'id': row['id'],
            'destination': row['destination_name'],
            'service': row['category_name'],
            'datetime': f"{row['booking_date']} {row['start_time']}",
            'duration': f"{row['hours']} hours",
            'total_cost': f"{row['total_price']:.2f}",
            'status': row['status']
        })
    
    summary = {
        'total': len(bookings),
        'pending': sum(1 for b in bookings if b['status'] == 'pending'),
        'accepted': sum(1 for b in bookings if b['status'] == 'accepted'),
        'rejected': sum(1 for b in bookings if b['status'] == 'rejected'),
        'paid': sum(1 for b in bookings if b['status'] == 'paid')
    }
    
    return render_template('user/status_table.html', bookings=bookings, summary=summary)

@app.route('/status-columns')
@login_required
def status_columns():
    """Card View of Bookings"""
    # Reuse the same logic as status_table, just distinct endpoint
    return status_table().replace('user/status_table.html', 'user/status_columns.html')

# --- API Routes (For React/Frontend Logic) ---

@app.route('/api/catalog')
def get_catalog():
    """Get catalog data + availability"""
    db = get_db()
    cats = db.execute('SELECT * FROM categories').fetchall()
    dests = db.execute('SELECT * FROM destinations').fetchall()
    
    # Check what is booked TODAY
    today = datetime.now().strftime('%Y-%m-%d')
    booked = db.execute('''
        SELECT destination_id, category_id FROM bookings 
        WHERE booking_date = ? AND status IN ('accepted', 'paid')
    ''', (today,)).fetchall()
    
    booked_keys = set((b['destination_id'], b['category_id']) for b in booked)
    
    catalog = []
    for cat in cats:
        items = []
        for dest in dests:
            status = 'Not Available' if (dest['id'], cat['id']) in booked_keys else 'Available'
            items.append({
                'id': dest['id'],
                'name': dest['name'],
                'description': dest['description'],
                'status': status,
                'image': dest['image_url']
            })
        catalog.append({
            'id': cat['id'],
            'name': cat['name'],
            'description': cat['description'],
            'price': cat['price_per_hour'],
            'image': cat['image_url'],
            'items': items
        })
        
    return jsonify(catalog)

@app.route('/api/bookings', methods=['GET'])
@login_required
def list_bookings():
    """Get list of bookings (JSON)"""
    db = get_db()
    query = '''
        SELECT b.id, b.booking_date, b.start_time, b.hours, b.total_price, b.status,
               u.username as customer_name, d.name as destination_name, c.name as category_name
        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN destinations d ON b.destination_id = d.id
        JOIN categories c ON b.category_id = c.id
    '''
    
    if session['role'] == 'customer':
        query += ' WHERE b.user_id = ? ORDER BY b.created_at DESC'
        rows = db.execute(query, (session['user_id'],)).fetchall()
    else:
        query += ' ORDER BY b.created_at DESC'
        rows = db.execute(query).fetchall()
        
    return jsonify([dict(row) for row in rows])

@app.route('/api/bookings', methods=['POST'])
@login_required
def create_booking():
    """Create a new booking"""
    data = request.json
    dest_id = data.get('destination_id')
    cat_id = data.get('category_id')
    date = data.get('date')
    time = data.get('time')
    hours = int(data.get('hours'))
    
    db = get_db()
    
    # Check availability
    exists = db.execute('''
        SELECT id FROM bookings 
        WHERE destination_id = ? AND category_id = ? AND booking_date = ? 
        AND status IN ('accepted', 'paid')
    ''', (dest_id, cat_id, date)).fetchone()
    
    if exists:
        return jsonify({'error': 'Already booked for this date.'}), 409
        
    # Calculate price
    cat = db.execute('SELECT price_per_hour FROM categories WHERE id = ?', (cat_id,)).fetchone()
    total = cat['price_per_hour'] * hours
    
    db.execute('''
        INSERT INTO bookings (user_id, destination_id, category_id, booking_date, start_time, hours, total_price, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)
    ''', (session['user_id'], dest_id, cat_id, date, time, hours, total, datetime.now()))
    db.commit()
    
    return jsonify({'message': 'Booking request sent.'})

@app.route('/api/bookings/<int:id>/status', methods=['PUT'])
@role_required('admin')
def update_booking_status(id):
    """Admin: Accept/Reject booking"""
    status = request.json.get('status')
    db = get_db()
    db.execute('UPDATE bookings SET status = ? WHERE id = ?', (status, id))
    db.commit()
    return jsonify({'message': f'Booking {status}.'})

@app.route('/api/bookings/<int:id>/pay', methods=['POST'])
@login_required
def pay_booking(id):
    """Customer: Pay for booking"""
    db = get_db()
    # Check ownership
    booking = db.execute('SELECT * FROM bookings WHERE id = ?', (id,)).fetchone()
    if not booking or booking['user_id'] != session['user_id']:
        return jsonify({'error': 'Booking not found'}), 404
        
    if booking['status'] != 'accepted':
        return jsonify({'error': 'Can only pay for accepted bookings.'}), 400
        
    db.execute("UPDATE bookings SET status = 'paid' WHERE id = ?", (id,))
    db.commit()
    return jsonify({'message': 'Payment successful!'})

# --- Settings API (Admin Only) ---

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get all settings"""
    db = get_db()
    return jsonify({
        'destinations': [dict(d) for d in db.execute('SELECT * FROM destinations').fetchall()],
        'categories': [dict(c) for c in db.execute('SELECT * FROM categories').fetchall()]
    })

@app.route('/api/settings/<type>', methods=['POST'])
@role_required('admin')
def add_setting(type):
    """Add item"""
    name = request.form.get('name')
    desc = request.form.get('description')
    image = request.files.get('image')
    
    # Image saving logic
    image_url = ''
    if image and image.filename:
        path = os.path.join('static', 'uploads', image.filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        image.save(path)
        image_url = f'/static/uploads/{image.filename}'
        
    db = get_db()
    try:
        if type == 'destination':
            db.execute('INSERT INTO destinations (name, description, image_url) VALUES (?, ?, ?)', (name, desc, image_url))
        elif type == 'category':
             db.execute('INSERT INTO categories (name, description, image_url) VALUES (?, ?, ?)', (name, desc, image_url))
        db.commit()
        return jsonify({'message': 'Added.'})
    except:
        return jsonify({'error': 'Name exists.'}), 400

@app.route('/api/settings/<type>/<int:id>', methods=['PUT'])
@role_required('admin')
def update_setting(type, id):
    """Update item"""
    data = request.json
    name = data.get('name')
    desc = data.get('description')
    img = data.get('image_url')
    
    db = get_db()
    table = 'destinations' if type == 'destination' else 'categories'
    
    try:
        db.execute(f'UPDATE {table} SET name = ?, description = ?, image_url = ? WHERE id = ?', (name, desc, img, id))
        db.commit()
        return jsonify({'message': 'Updated.'})
    except:
        return jsonify({'error': 'Name exists.'}), 400

@app.route('/api/settings/<type>/<int:id>', methods=['DELETE'])
@role_required('admin')
def delete_setting(type, id):
    """Delete item"""
    db = get_db()
    table = 'destinations' if type == 'destination' else 'categories'
    db.execute(f'DELETE FROM {table} WHERE id = ?', (id,))
    db.commit()
    return jsonify({'message': 'Deleted.'})

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        with app.app_context():
            init_db()
    app.run(debug=True, port=5000)

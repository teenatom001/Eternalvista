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


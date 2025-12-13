import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'instance', 'eternaal.sqlite')

def seed_dublin():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    print("Seeding Dublin, Ireland...")

    # 1. Insert Destination
    cursor.execute('''
        INSERT INTO destination (name, description, image_url, availability)
        VALUES (?, ?, ?, ?)
    ''', (
        'Dublin, Ireland',
        'Experience the warmth and history of the Fair City. From historic castles to lively city center luxury, Dublin offers a perfect blend of tradition and modern elegance for your special day.',
        'https://images.unsplash.com/photo-1549918864-48ac978761a4?auto=format&fit=crop&w=1950&q=80',
        1
    ))
    dest_id = cursor.lastrowid
    print(f"Added Destination: Dublin (ID: {dest_id})")

    # 2. Insert Venues
    venues = [
        {
            'name': 'The Shelbourne',
            'capacity': 300,
            'price': 5000.00,
            'image_url': 'https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1950&q=80'
        },
        {
            'name': 'Dublin Castle',
            'capacity': 150,
            'price': 3500.00,
            'image_url': 'https://images.unsplash.com/photo-1533929736472-11199a9e3478?auto=format&fit=crop&w=1950&q=80'
        },
        {
            'name': 'Cliff at Lyons',
            'capacity': 200,
            'price': 4200.00,
            'image_url': 'https://images.unsplash.com/photo-1464207687429-7505649dae38?auto=format&fit=crop&w=1950&q=80'
        }
    ]

    for v in venues:
        cursor.execute('''
            INSERT INTO venue (destination_id, name, capacity, price, image_url, availability)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (dest_id, v['name'], v['capacity'], v['price'], v['image_url'], 1))
        print(f"  - Added Venue: {v['name']}")

    conn.commit()
    conn.close()
    print("Done!")

if __name__ == '__main__':
    seed_dublin()

import sqlite3
from eternaal.db import get_db
from eternaal import create_app

app = create_app()

def seed():
    with app.app_context():
        db = get_db()
        
        # Check if we already have data
        if db.execute('SELECT id FROM destination').fetchone():
            print("Data already exists.")
            return

        print("Seeding Dublin data...")
        
        # 1. Create Destination: Dublin
        # We'll treat this as the main "Destination" entry for the Dublin setup
        cur = db.execute(
            'INSERT INTO destination (name, description, image_url, availability) VALUES (?, ?, ?, ?)',
            ('Dublin, Ireland', 'Historic streets, lively pubs, and ancient castles.', 'https://images.unsplash.com/photo-1549918864-48ac978761a4?auto=format&fit=crop&w=800&q=80', 1)
        )
        dublin_id = cur.lastrowid

        # 2. Venues in Dublin
        venues = [
            # Name, Capacity, Price, Image
            ('Dublin Castle', 150, 2500.0, 'https://images.unsplash.com/photo-1590059390247-410a563ce2f9?auto=format&fit=crop&w=800&q=80'),
            ('Trinity College Library', 50, 1200.0, 'https://images.unsplash.com/photo-1547402633-40c21356f10c?auto=format&fit=crop&w=800&q=80'),
            ('Guinness Storehouse (Gravity Bar)', 200, 3000.0, 'https://images.unsplash.com/photo-1618428383389-c4398325a22d?auto=format&fit=crop&w=800&q=80'),
            ('St. Patrick\'s Cathedral', 300, 1800.0, 'https://images.unsplash.com/photo-1571665673059-e31d41a5477c?auto=format&fit=crop&w=800&q=80'),
        ]

        for v in venues:
            db.execute(
                'INSERT INTO venue (destination_id, name, capacity, price, image_url, availability) VALUES (?, ?, ?, ?, ?, ?)',
                (dublin_id, v[0], v[1], v[2], v[3], 1)
            )

        db.commit()
        print("Seeding complete!")

if __name__ == '__main__':
    seed()

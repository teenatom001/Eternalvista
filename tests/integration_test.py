
# Integration Test Script
# Simulates a full user flow: 
# 1. Admin adds data.
# 2. User books.
# 3. Admin accepts.

import unittest
import json
import sys
import os
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from eternaal import create_app
from eternaal.db import init_db

class IntegrationTestCase(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for testing
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        self.app = create_app({
            'TESTING': True,
            'DATABASE': self.db_path,
        })
        self.client = self.app.test_client()
        
        with self.app.app_context():
            init_db()
    
    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def login(self, username, password):
        return self.client.post('/login', 
            json={'username': username, 'password': password},
            content_type='application/json'
        )

    def register(self, username, password):
        return self.client.post('/register',
            json={'username': username, 'password': password},
            content_type='application/json'
        )

    def logout(self):
        return self.client.get('/logout')

    def test_full_scenario(self):
        # 1. Admin setup
        print("Step 1: Admin creates Destination and Venue")
        # Login as admin (created by init_db)
        self.login('admin', 'admin')
        
        self.client.post('/api/destinations', json={'name': 'Bali', 'description': 'Island', 'availability': True})
        self.client.post('/api/venues', json={'destination_id': 1, 'name': 'Beach Resort', 'capacity': 50, 'price': 1000})
        
        self.logout()
        
        # 2. User checks availability
        print("Step 2: User lists venues")
        # User doesn't technically need to be logged in to view venues (based on routes.py)
        res = self.client.get('/api/venues?destination_id=1')
        venues = json.loads(res.data)
        self.assertEqual(len(venues), 1)
        venue_id = venues[0]['id']

        # 3. User Books
        print("Step 3: User makes a booking")
        # Register and login as user
        self.register('Alice', 'password')
        self.login('Alice', 'password')
        
        res = self.client.post('/api/bookings', json={
            'customer_name': 'Alice',
            'destination_id': 1,
            'venue_id': venue_id,
            'booking_date': '2024-12-25'
        })
        self.assertEqual(res.status_code, 201)
        
        self.logout()

        # 4. Admin Checks Bookings
        print("Step 4: Admin views booking")
        self.login('admin', 'admin')
        
        res = self.client.get('/api/bookings')
        bookings = json.loads(res.data)
        booking_id = bookings[0]['id']
        self.assertEqual(bookings[0]['status'], 'pending')

        # 5. Admin Accepts
        print("Step 5: Admin accepts booking")
        self.client.patch(f'/api/bookings/{booking_id}', json={'status': 'accepted'})
        
        # 6. Verify Final State
        res = self.client.get('/api/bookings')
        bookings = json.loads(res.data)
        self.assertEqual(bookings[0]['status'], 'accepted')
        print("Integration Scenario Completed Successfully.")

if __name__ == '__main__':
    unittest.main()

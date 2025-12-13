import pytest
import json
import os
import tempfile
from eternaal import create_app
from eternaal.db import get_db, init_db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


def login_as_admin(client):
    """Helper function to login as admin"""
    return client.post('/login', 
        json={'username': 'admin', 'password': 'admin'},
        content_type='application/json'
    )


class TestIntegration:
    """Integration tests for frontend-to-backend-to-database flow"""
    
    def test_frontend_to_backend_flow(self, client, app):
        """
        Integration test: Frontend → API → Database → Response
        
        This test simulates the complete flow:
        1. Frontend sends fetch() request
        2. Backend API processes request
        3. Data is persisted to database
        4. Response is returned as JSON
        5. Frontend receives and can update DOM
        """
        with client:
            # Step 1: Login (simulating frontend login)
            login_response = login_as_admin(client)
            assert login_response.status_code == 200
            
            # Step 2: Frontend sends POST request to create destination
            create_response = client.post('/api/destinations', 
                json={
                    'name': 'Integration Test Destination',
                    'description': 'Testing full stack integration',
                    'image_url': 'https://example.com/test.jpg'
                },
                content_type='application/json'
            )
            
            # Step 3: Verify API response
            assert create_response.status_code == 201
            assert create_response.content_type == 'application/json'
            create_data = json.loads(create_response.data)
            assert 'message' in create_data
            
            # Step 4: Verify data was persisted to database
            # Frontend would now fetch to update DOM
            get_response = client.get('/api/destinations')
            assert get_response.status_code == 200
            destinations = json.loads(get_response.data)
            
            # Verify our destination is in the database
            assert any(d['name'] == 'Integration Test Destination' for d in destinations)
            
            # Step 5: Verify data integrity
            test_dest = next(d for d in destinations if d['name'] == 'Integration Test Destination')
            assert test_dest['description'] == 'Testing full stack integration'
            assert test_dest['image_url'] == 'https://example.com/test.jpg'
            assert 'id' in test_dest
            assert 'availability' in test_dest

    def test_complete_booking_integration(self, client, app):
        """
        Integration test for complete booking workflow
        
        Tests the full user journey:
        1. View available destinations
        2. View venues for a destination
        3. Create a booking
        4. Admin views booking
        5. Admin updates booking status
        """
        with client:
            # Login as admin
            login_as_admin(client)
            
            # 1. Create destination (admin action)
            client.post('/api/destinations', 
                json={
                    'name': 'Dublin',
                    'description': 'Historic Irish capital',
                    'image_url': 'https://example.com/dublin.jpg'
                },
                content_type='application/json'
            )
            
            # 2. Create venue (admin action)
            client.post('/api/venues', 
                json={
                    'destination_id': 1,
                    'name': 'Trinity College',
                    'capacity': 150,
                    'price': 7500.0
                },
                content_type='application/json'
            )
            
            # 3. Customer views destinations (public endpoint)
            dest_response = client.get('/api/destinations')
            assert dest_response.status_code == 200
            destinations = json.loads(dest_response.data)
            assert len(destinations) >= 1
            
            # 4. Customer views venues for destination
            venue_response = client.get('/api/venues?destination_id=1')
            assert venue_response.status_code == 200
            venues = json.loads(venue_response.data)
            assert len(venues) >= 1
            
            # 5. Customer creates booking
            booking_response = client.post('/api/bookings', 
                json={
                    'customer_name': 'Alice Johnson',
                    'customer_email': 'alice@example.com',
                    'destination_id': 1,
                    'venue_id': 1,
                    'booking_date': '2025-08-20'
                },
                content_type='application/json'
            )
            assert booking_response.status_code == 201
            
            # 6. Admin views all bookings
            bookings_response = client.get('/api/bookings')
            assert bookings_response.status_code == 200
            bookings = json.loads(bookings_response.data)
            assert len(bookings) >= 1
            
            # Verify booking details
            booking = bookings[0]
            assert booking['customer_name'] == 'Alice Johnson'
            assert booking['status'] == 'pending'
            assert 'dest_name' in booking
            assert 'venue_name' in booking
            
            # 7. Admin updates booking status
            update_response = client.patch('/api/bookings/1', 
                json={'status': 'accepted'},
                content_type='application/json'
            )
            assert update_response.status_code == 200
            
            # 8. Verify status was updated
            final_bookings = client.get('/api/bookings')
            final_data = json.loads(final_bookings.data)
            assert final_data[0]['status'] == 'accepted'

    def test_api_error_handling(self, client, app):
        """Test that API properly handles errors"""
        with client:
            login_as_admin(client)
            
            # Test missing required fields
            response = client.post('/api/destinations', 
                json={'name': 'Test'},  # Missing description
                content_type='application/json'
            )
            assert response.status_code == 400
            
            # Test creating venue with invalid destination_id
            response = client.post('/api/venues', 
                json={
                    'destination_id': 999,  # Non-existent
                    'name': 'Test Venue',
                    'capacity': 100,
                    'price': 1000.0
                },
                content_type='application/json'
            )
            # Should fail due to foreign key constraint or validation
            assert response.status_code in [400, 500]

    def test_availability_checking(self, client, app):
        """Test that availability is properly checked before booking"""
        with client:
            login_as_admin(client)
            
            # Create destination with availability = 0
            with app.app_context():
                db = get_db()
                db.execute(
                    'INSERT INTO destination (name, description, availability) VALUES (?, ?, ?)',
                    ('Unavailable Dest', 'Not available', 0)
                )
                db.execute(
                    'INSERT INTO venue (destination_id, name, capacity, price, availability) VALUES (?, ?, ?, ?, ?)',
                    (1, 'Test Venue', 100, 1000.0, 1)
                )
                db.commit()
            
            # Try to book unavailable destination
            response = client.post('/api/bookings', 
                json={
                    'customer_name': 'Test User',
                    'customer_email': 'test@example.com',
                    'destination_id': 1,
                    'venue_id': 1,
                    'booking_date': '2025-09-01'
                },
                content_type='application/json'
            )
            
            # Should be rejected
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'unavailable' in data['error'].lower()

import pytest
import json
import os
import tempfile
from eternaal import create_app
from eternaal.db import get_db, init_db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    # Create the database and load test data
    with app.app_context():
        init_db()

    yield app

    # Clean up
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


def login_as_admin(client):
    """Helper function to login as admin"""
    return client.post('/login', 
        json={'username': 'admin', 'password': 'admin'},
        content_type='application/json'
    )


class TestDestinationCRUD:
    """Test CRUD operations for Destinations"""
    
    def test_create_destination(self, client, app):
        """Test creating a new destination"""
        # Login as admin first
        with client:
            login_as_admin(client)
            
            response = client.post('/api/destinations', 
                json={
                    'name': 'Hawaii',
                    'description': 'Tropical paradise',
                    'image_url': 'https://example.com/hawaii.jpg'
                },
                content_type='application/json'
            )
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['message'] == 'Destination created'

    def test_get_destinations(self, client, app):
        """Test retrieving all destinations"""
        # Login and create a destination first
        with client:
            login_as_admin(client)
            client.post('/api/destinations', 
                json={'name': 'Kyoto', 'description': 'Ancient city'},
                content_type='application/json'
            )
            
            # Now get all destinations
            response = client.get('/api/destinations')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) >= 1
            assert any(d['name'] == 'Kyoto' for d in data)


    def test_update_destination(self, client, app):
        """Test updating a destination"""
        with client:
            login_as_admin(client)
            
            # Create destination
            client.post('/api/destinations', 
                json={'name': 'Original Name', 'description': 'Original Description'},
                content_type='application/json'
            )
            
            # Get the ID
            response = client.get('/api/destinations')
            data = json.loads(response.data)
            dest_id = next(d['id'] for d in data if d['name'] == 'Original Name')
            
            # Update it
            response = client.put(f'/api/destinations/{dest_id}',
                json={'name': 'Updated Name', 'description': 'Updated Description'},
                content_type='application/json'
            )
            assert response.status_code == 200
            
            # Verify update
            response = client.get('/api/destinations')
            data = json.loads(response.data)
            updated = next(d for d in data if d['id'] == dest_id)
            assert updated['name'] == 'Updated Name'
            assert updated['description'] == 'Updated Description'
    
    def test_delete_destination(self, client, app):
        """Test deleting a destination"""
        with client:
            login_as_admin(client)
            
            # Create destination
            client.post('/api/destinations', 
                json={'name': 'TestDest', 'description': 'Test'},
                content_type='application/json'
            )
            
            # Get the ID
            response = client.get('/api/destinations')
            data = json.loads(response.data)
            dest_id = next(d['id'] for d in data if d['name'] == 'TestDest')
            
            # Delete it
            response = client.delete(f'/api/destinations/{dest_id}')
            assert response.status_code == 200


class TestVenueCRUD:
    """Test CRUD operations for Venues"""
    
    def test_create_venue(self, client, app):
        """Test creating a new venue"""
        with client:
            login_as_admin(client)
            
            # Create destination first
            client.post('/api/destinations', 
                json={'name': 'Paris', 'description': 'City of Love'},
                content_type='application/json'
            )
            
            # Create venue
            response = client.post('/api/venues', 
                json={
                    'destination_id': 1,
                    'name': 'Eiffel Tower',
                    'capacity': 100,
                    'price': 5000.0
                },
                content_type='application/json'
            )
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['message'] == 'Venue created'

    def test_get_venues(self, client, app):
        """Test retrieving venues"""
        with client:
            login_as_admin(client)
            
            # Create destination and venue
            client.post('/api/destinations', 
                json={'name': 'Rome', 'description': 'Eternal City'},
                content_type='application/json'
            )
            client.post('/api/venues', 
                json={
                    'destination_id': 1,
                    'name': 'Colosseum',
                    'capacity': 200,
                    'price': 8000.0
                },
                content_type='application/json'
            )
            
            # Get venues
            response = client.get('/api/venues')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) >= 1
    
    def test_update_venue(self, client, app):
        """Test updating a venue"""
        with client:
            login_as_admin(client)
            
            # Create destination and venue
            client.post('/api/destinations', 
                json={'name': 'London', 'description': 'Historic City'},
                content_type='application/json'
            )
            client.post('/api/venues', 
                json={
                    'destination_id': 1,
                    'name': 'Original Venue',
                    'capacity': 50,
                    'price': 2000.0
                },
                content_type='application/json'
            )
            
            # Get venue ID
            response = client.get('/api/venues')
            venues = json.loads(response.data)
            venue_id = next(v['id'] for v in venues if v['name'] == 'Original Venue')
            
            # Update venue
            response = client.put(f'/api/venues/{venue_id}',
                json={
                    'destination_id': 1,
                    'name': 'Updated Venue',
                    'capacity': 100,
                    'price': 3000.0
                },
                content_type='application/json'
            )
            assert response.status_code == 200
            
            # Verify update
            response = client.get('/api/venues')
            venues = json.loads(response.data)
            updated = next(v for v in venues if v['id'] == venue_id)
            assert updated['name'] == 'Updated Venue'
            assert updated['capacity'] == 100
            assert updated['price'] == 3000.0


class TestBookingFlow:
    """Test complete booking workflow"""
    
    def test_create_booking_flow(self, client, app):
        """Test the complete booking creation flow"""
        with client:
            # Login as admin
            login_as_admin(client)
            
            # 1. Create Destination
            client.post('/api/destinations', 
                json={'name': 'Paris', 'description': 'Romantic'},
                content_type='application/json'
            )
            
            # 2. Create Venue
            client.post('/api/venues', 
                json={
                    'destination_id': 1,
                    'name': 'Eiffel Tower',
                    'capacity': 100,
                    'price': 5000.0
                },
                content_type='application/json'
            )
            
            # 3. Create Booking
            response = client.post('/api/bookings', 
                json={
                    'customer_name': 'John Doe',
                    'customer_email': 'john@example.com',
                    'destination_id': 1,
                    'venue_id': 1,
                    'booking_date': '2025-06-01'
                },
                content_type='application/json'
            )
            
            assert response.status_code == 201
            
            # 4. Verify booking was created
            response = client.get('/api/bookings')
            data = json.loads(response.data)
            assert len(data) >= 1
            assert data[0]['status'] == 'pending'

    def test_update_booking_status(self, client, app):
        """Test updating booking status"""
        with client:
            login_as_admin(client)
            
            # Create destination, venue, and booking
            client.post('/api/destinations', 
                json={'name': 'Tokyo', 'description': 'Modern'},
                content_type='application/json'
            )
            client.post('/api/venues', 
                json={
                    'destination_id': 1,
                    'name': 'Tokyo Tower',
                    'capacity': 50,
                    'price': 3000.0
                },
                content_type='application/json'
            )
            client.post('/api/bookings', 
                json={
                    'customer_name': 'Jane Smith',
                    'customer_email': 'jane@example.com',
                    'destination_id': 1,
                    'venue_id': 1,
                    'booking_date': '2025-07-15'
                },
                content_type='application/json'
            )
            
            # Update booking status
            response = client.patch('/api/bookings/1', 
                json={'status': 'accepted'},
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Booking updated'

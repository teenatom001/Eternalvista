import pytest
import os
import tempfile
from app import app, init_db, get_db

@pytest.fixture
def client():
    """Create a test client for the app."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    app.config['DATABASE'] = db_path
    
    # Enable testing mode
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            # Initialize the temp DB
            init_db()
        yield client
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

def test_home_page(client):
    """Integration Test: Check if home page loads."""
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'EternalVista' in rv.data

def test_api_crud_destination(client):
    """CRUD Test: Add and Read a destination."""
    
    # 1. Login as Admin
    # (We bypass login for simplicity if we can, or we simulate session)
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'admin'

    # 2. CREATE (POST)
    data = {'name': 'TestCity', 'description': 'A test place'}
    rv = client.post('/api/settings/destination', data=data)
    assert rv.status_code == 200
    assert b'Added.' in rv.data

    # 3. READ (GET)
    rv = client.get('/api/settings')
    assert rv.status_code == 200
    assert b'TestCity' in rv.data

def test_api_delete_destination(client):
    """CRUD Test: Delete a destination."""
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'admin'

    # First add one
    client.post('/api/settings/destination', data={'name': 'To Delete', 'description': '...'})
    
    # Get ID (Assuming it's the latest or knowing seeding adds 3, so this is 4)
    # Ideally we parse JSON, but let's just assume ID 4 for this simple test
    # or better, fetch and find
    rv = client.get('/api/settings')
    json_data = rv.get_json()
    target_id = json_data['destinations'][-1]['id']

    # DELETE
    rv = client.delete(f'/api/settings/destination/{target_id}')
    assert rv.status_code == 200
    assert b'Deleted.' in rv.data

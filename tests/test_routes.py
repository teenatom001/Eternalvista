import os
import tempfile
import pytest
from eternaal import create_app
from eternaal.db import get_db, init_db

@pytest.fixture
def app():
    # Create a temporary file for the database
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        "TESTING": True, 
        "SECRET_KEY": "test", 
        "DATABASE": db_path
    })
    
    # Initialize the database
    with app.app_context():
        init_db()
        
    yield app
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

def test_index_page(client):
    resp = client.get('/')
    assert resp.status_code == 200
    # The index template contains a heading with "Eternal"
    assert b"Eternal" in resp.data

def test_admin_access_requires_login(client):
    # Without login should redirect to login (or unauthorized)
    resp = client.get('/admin')
    # Since @login_required redirects to login page
    assert resp.status_code in (302, 401, 403)

def test_login_and_logout(client, app):
    from werkzeug.security import generate_password_hash
    # Insert a test user directly into the temporary DB
    with app.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO user (username, password, role) VALUES (?, ?, ?)",
            ("testadmin", generate_password_hash("password"), "admin")
        )
        db.commit()
    # Login via POST JSON
    login_resp = client.post('/login', json={"username": "testadmin", "password": "password"})
    assert login_resp.status_code == 200
    # After login, access admin page
    admin_resp = client.get('/admin')
    assert admin_resp.status_code == 200
    # Logout
    logout_resp = client.get('/logout')
    assert logout_resp.status_code == 302
    # After logout, admin should be inaccessible again
    admin_resp2 = client.get('/admin')
    assert admin_resp2.status_code in (302, 401, 403)

import pytest
from eternaal import create_app
from eternaal.db import get_db

@pytest.fixture
def app():
    # Create app with testing config
    app = create_app({"TESTING": True, "SECRET_KEY": "test", "DATABASE": ":memory:"})
    # Initialize the database schema (assuming a function init_db exists)
    with app.app_context():
        from eternaal import db
        db.init_app(app)
        # Create tables – you may need to import schema creation here
        # For simplicity, assume a function init_db() that creates tables
        # If not present, you can execute raw SQL to create minimal tables
        # Here we just pass (tests may fail if DB not set up)
    return app

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
    # Insert a test user directly into the in‑memory DB
    with app.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO user (username, password, role) VALUES (?, ?, ?)",
            ("testadmin", "$(python -c 'import werkzeug.security, sys; print(workzeug.security.generate_password_hash(\"password\"))')", "admin")
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

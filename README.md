





## Project Overview

### Organization: EternalVista

**Business Context:**  
EternalVista is a small wedding destination planning company that specializes in organizing destination weddings across Ireland. The company manages multiple wedding destinations (Dublin, Wicklow, Cork) and provides various wedding venues at each location.

**Problem Statement:**  
The company currently manages bookings manually through spreadsheets and phone calls, leading to:
- Double bookings and scheduling conflicts
- Difficulty tracking venue availability
- Inefficient customer communication
- No centralized data management

**Solution:**  
A web-based Information System that provides:
- Centralized database for destinations, venues, and bookings
- Real-time availability checking
- Admin dashboard for managing all resources
- Customer booking interface
- Full CRUD operations for all entities

---

## System Requirements

### Functional Requirements

#### 1. **Destination Management** (CRUD)
- **Create:** Admin can add new wedding destinations
- **Read:** View all available destinations with details
- **Update:** Modify destination information
- **Delete:** Remove destinations from the system

#### 2. **Venue Management** (CRUD)
- **Create:** Admin can add venues to destinations
- **Read:** View venues filtered by destination
- **Update:** Modify venue details (capacity, price, availability)
- **Delete:** Remove venues from the system

#### 3. **Booking Management** (CRUD)
- **Create:** Customers can create booking requests
- **Read:** View all bookings (admin) or own bookings (customer)
- **Update:** Admin can update booking status (pending/accepted/rejected/paid)
- **Delete:** Admin can cancel bookings

#### 4. **User Authentication**
- Login system for admin users
- Role-based access control (admin vs. public)
- Session management

#### 5. **Availability Checking**
- Real-time validation of destination/venue availability
- Prevent double bookings
- Display availability status to users

### Non-Functional Requirements

- **Usability:** Simple, intuitive interface
- **Performance:** Fast API responses (<500ms)
- **Security:** Password hashing, session management
- **Data Integrity:** Foreign key constraints, validation
- **Maintainability:** Modular code structure, clear documentation

---

## Architecture

### System Architecture Pattern: **RESTful API with Frontend-Backend Separation**

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (HTML/JS)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  index.html  │  │  admin.html  │  │  login.html  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                    fetch() API Calls                         │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   Flask API     │
                    │   (routes.py)   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Database      │
                    │   (SQLite)      │
                    └─────────────────┘
```

**Key Architectural Decisions:**

1. **API-First Design:** All data operations go through REST API endpoints
2. **No Page Refreshes:** Frontend uses `fetch()` for all CRUD operations
3. **Separation of Concerns:** 
   - `routes.py` - API endpoints
   - `auth.py` - Authentication logic
   - `db.py` - Database operations
   - `templates/` - HTML views
   - `static/js/` - Frontend JavaScript

4. **Stateless API:** Each request contains all necessary information
5. **JSON Communication:** All API requests/responses use JSON format

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/[YOUR-USERNAME]/eternaal.git
cd eternaal
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Mac/Linux
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Initialize Database
```bash
python -c "from eternaal import create_app; from eternaal.db import init_db; app = create_app(); app.app_context().push(); init_db()"
```

### Step 5: Run the Application
```bash
python app.py
```

The application will be available at: `http://127.0.0.1:5000`

### Default Admin Credentials
- **Username:** admin
- **Password:** admin123

---

## CRUD Operations

### 1. Destinations CRUD

#### Create Destination
```javascript
// Frontend (JavaScript)
fetch('/api/destinations', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        name: 'Dublin',
        description: 'Historic city weddings',
        image_url: 'https://example.com/dublin.jpg'
    })
});
```

```python
# Backend (routes.py)
@bp.route('/api/destinations', methods=['POST'])
@login_required
def create_destination():
    data = request.get_json()
    db = get_db()
    db.execute('INSERT INTO destination (name, description, image_url, availability) VALUES (?, ?, ?, ?)',
               (data['name'], data['description'], data.get('image_url'), 1))
    db.commit()
    return jsonify({'message': 'Destination created'}), 201
```

#### Read Destinations
```javascript
// Frontend
fetch('/api/destinations')
    .then(res => res.json())
    .then(data => console.log(data));
```

```python
# Backend
@bp.route('/api/destinations', methods=['GET'])
def get_destinations():
    db = get_db()
    dests = db.execute('SELECT * FROM destination').fetchall()
    return jsonify([dict(d) for d in dests])
```

#### Update Destination
```javascript
// Frontend
fetch(`/api/destinations/${id}`, {
    method: 'PUT',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        name: 'Updated Name',
        description: 'New Description',
        image_url: 'https://example.com/new.jpg'
    })
});
```

```python
# Backend
@bp.route('/api/destinations/<int:id>', methods=['PUT'])
@login_required
def update_destination(id):
    # ... validation logic ...
    db.execute('UPDATE destination SET name = ?, description = ? WHERE id = ?',
               (data['name'], data['description'], id))
    db.commit()
    return jsonify({'message': 'Destination updated'}), 200
```

#### Delete Destination
```javascript
// Frontend
fetch(`/api/destinations/${id}`, {method: 'DELETE'});
```

```python
# Backend
@bp.route('/api/destinations/<int:id>', methods=['DELETE'])
@login_required
def delete_destination(id):
    db = get_db()
    db.execute('DELETE FROM destination WHERE id = ?', (id,))
    db.commit()
    return jsonify({'message': 'Deleted'}), 200
```

### 2. Venues CRUD

#### Create Venue
```python
# Backend
@bp.route('/api/venues', methods=['POST'])
@login_required
def create_venue():
    # ... validation ...
    db.execute('INSERT INTO venue ... VALUES (...)')
    return jsonify({'message': 'Venue created'}), 201
```

#### Read Venues
```javascript
// Frontend: Get all venues for a destination
fetch('/api/venues?destination_id=1')
```

#### Update Venue
```http
PUT /api/venues/1
Content-Type: application/json
{ "name": "Grand Ballroom", "capacity": 300, ... }
```

#### Delete Venue
```http
DELETE /api/venues/1
```

### 3. Bookings CRUD

Similar pattern to Destinations - see `routes.py` lines 85-150

---

## Testing

### Unit Tests

Located in `tests/test_app.py` - Tests individual CRUD functions:

```bash
# Run unit tests
pytest tests/test_app.py -v
```

**Test Coverage:**
- ✅ `test_create_destination()` - Tests POST /api/destinations
- ✅ `test_get_destinations()` - Tests GET /api/destinations
- ✅ `test_create_booking_flow()` - Tests complete booking workflow

### Integration Tests

Located in `tests/test_integration.py` - Tests frontend-to-backend interaction:

```bash
# Run integration tests
pytest tests/test_integration.py -v
```

**Integration Test:**
- ✅ Frontend → API → Database flow
- ✅ Validates data persistence
- ✅ Tests API response formats

### Running All Tests
```bash
pytest tests/ -v
```

---

## API Documentation

### Base URL
```
http://127.0.0.1:5000
```

### Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/api/destinations` | No | Get all destinations |
| POST | `/api/destinations` | Yes (Admin) | Create destination |
| PUT | `/api/destinations/<id>` | Yes (Admin) | Update destination |
| DELETE | `/api/destinations/<id>` | Yes (Admin) | Delete destination |
| GET | `/api/venues` | No | Get all venues |
| GET | `/api/venues?destination_id=<id>` | No | Get venues by destination |
| POST | `/api/venues` | Yes (Admin) | Create venue |
| PUT | `/api/venues/<id>` | Yes (Admin) | Update venue |
| DELETE | `/api/venues/<id>` | Yes (Admin) | Delete venue |
| GET | `/api/bookings` | Yes | Get bookings |
| POST | `/api/bookings` | Yes | Create booking |
| PATCH | `/api/bookings/<id>` | Yes (Admin) | Update booking status |
| DELETE | `/api/bookings/<id>` | Yes (Admin) | Delete booking |

### Example API Requests

#### Create Booking
```http
POST /api/bookings
Content-Type: application/json

{
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "destination_id": 1,
    "venue_id": 2,
    "booking_date": "2025-06-15"
}
```

**Response:**
```json
{
    "message": "Booking created"
}
```

---

## Technology Stack

### Backend
- **Flask 3.1.2** - Web framework
- **SQLite** - Database
- **Werkzeug** - Password hashing & security
- **Python 3.13** - Programming language

### Frontend
- **HTML5** - Structure
- **Vanilla JavaScript** - Logic (fetch API)
- **CSS3** - Styling (Bootstrap 5)

### Testing
- **pytest 9.0.2** - Testing framework

### Development Tools
- **Git/GitHub** - Version control
- **VS Code** - IDE
- **Virtual Environment** - Dependency isolation

---

## Project Structure

```
eternaal/
├── app.py                  # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
│
├── eternaal/              # Main application package
│   ├── __init__.py        # App factory
│   ├── auth.py            # Authentication logic
│   ├── db.py              # Database operations
│   ├── routes.py          # API endpoints
│   ├── schema.sql         # Database schema
│   │
│   ├── templates/         # HTML templates
│   │   ├── base.html
│   │   ├── index.html     # Public homepage
│   │   ├── admin.html     # Admin dashboard
│   │   └── login.html     # Login page
│   │
│   └── static/            # Static files
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js     # Frontend JavaScript
│
├── tests/                 # Test files
│   ├── test_app.py        # Unit tests
│   └── test_integration.py # Integration tests
│
├── instance/              # Instance-specific files
│   └── eternaal.sqlite    # SQLite database
│
└── venv/                  # Virtual environment (not in git)
```

---

## Database Schema

### Tables

#### 1. `user`
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'customer'
);
```

#### 2. `destination`
```sql
CREATE TABLE destination (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    image_url TEXT,
    availability INTEGER DEFAULT 1
);
```

#### 3. `venue`
```sql
CREATE TABLE venue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    capacity INTEGER,
    price REAL,
    availability INTEGER DEFAULT 1,
    FOREIGN KEY (destination_id) REFERENCES destination(id)
);
```

#### 4. `booking`
```sql
CREATE TABLE booking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    customer_email TEXT,
    destination_id INTEGER NOT NULL,
    venue_id INTEGER NOT NULL,
    booking_date TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY (destination_id) REFERENCES destination(id),
    FOREIGN KEY (venue_id) REFERENCES venue(id)
);
```

---


## Attributions

### External Libraries & Frameworks

1. **Flask** (BSD-3-Clause License)
   - Source: https://flask.palletsprojects.com/
   - Usage: Web framework for backend API
   - Integration: Used as the core framework for routing, request handling, and application structure

2. **Bootstrap 5** (MIT License)
   - Source: https://getbootstrap.com/
   - Usage: CSS framework for responsive design
   - Integration: Linked via CDN in base.html for styling components

3. **pytest** (MIT License)
   - Source: https://pytest.org/
   - Usage: Testing framework
   - Integration: Used for all unit and integration tests

4. **Werkzeug** (BSD-3-Clause License)
   - Source: https://werkzeug.palletsprojects.com/
   - Usage: Password hashing and security utilities
   - Integration: Used in auth.py for secure password storage



### Code Attribution

- Database schema design: Original student work
- API endpoint logic: Original student work with AI assistance for syntax
- Frontend JavaScript: Original student work
- Test cases: Original student work

---




---

## Future Enhancements

1. Email notifications for booking confirmations
2. Payment gateway integration
3. Customer review system
4. Photo gallery for venues
5. Calendar view for availability
6. Mobile responsive design improvements
7. Advanced search and filtering
8. Reporting dashboard for admin




# Documentation

## Module Details

| Item                      | Description                                        |
| ------------------------- | -------------------------------------------------- |
| **Module Title**          | Programming for Information Systems                |
| **Module Code**           | B9IS123                                            |
| **Programme/Cohort**      | 2526_TMD1                                          |
| **Assessment Number**     | 2                                                  |
| **Submission Components** | Code/Project (GitHub), Documentation, Presentation |
| **Student**               | Teena Tom                                          |

---

## Assignment Task: "Eternal" – destination wedding

### Selected Organization

**Name:** Eternal (formerly EternalVista)
**Business Context:** I designed this system for a boutique wedding planning agency in Ireland that manages exclusive venues across destinations such as Dublin, Wicklow, and Cork.
**Justification:** The organisation currently relies on manual processes such as spreadsheets and phone calls, which frequently leads to double bookings and inefficiencies. I identified that a web‑based CRUD system would solve this problem by centralising venue availability and booking management.

---

## Requirements of the Information System

### 1. Data Requirements (CRUD)

The system I developed manages the following entities with full Create, Read, Update, and Delete (CRUD) functionality:

* **Destinations** (e.g., Dublin, Cork)

  * *Create/Update/Delete:* Performed by Admin users only.
  * *Read:* Available to all users.

* **Venues** (e.g., Grand Ballroom, Garden Suite)

  * *Create/Update/Delete:* Admin only.
  * *Read:* Publicly available and linked to Destinations.

* **Bookings**

  * *Create:* Registered customers can submit booking requests.
  * *Read:* Customers can view only their own bookings, while Admins can view all bookings.
  * *Update:* Admins update booking status (Confirmed / Cancelled).
  * *Delete:* Admins can remove bookings when required.

* **Users**

  * *Read:* Admins can view registered users.
  * *Delete:* Admins can ban or remove users from the system.

---

### 2. User Roles & Validation

I implemented role‑based access control to ensure system security and correct usage:

* **Admin:** Has full access to manage destinations, venues, users, and all bookings.
* **Customer:** Can browse destinations and venues, view only their own bookings, and create new booking requests.

**Validation Rules Implemented:**

* **Availability Checks:** The system prevents double booking of the same venue on the same date.
* **Input Validation:** All forms validate required fields, valid dates, and logical constraints before submission.

---

## System Architecture

The application follows the required **API‑First Architecture**, which I implemented as follows:

### 1. Backend (API Provider)

* Built using **Flask (Python)** and **SQLite**.
* Provides REST‑style JSON endpoints such as `GET /api/destinations` and `POST /api/bookings`.
* Handles all database operations, session management, authentication, and business rules including availability checking.

### 2. Frontend (API Consumer)

* Developed using **HTML5, Bootstrap 5, and Vanilla JavaScript**.
* The frontend consumes backend APIs using JavaScript `fetch()` calls.
* Main content is not rendered directly using Jinja templates; instead, JSON data is retrieved asynchronously and injected into the DOM.
* CRUD operations occur without page refreshes, providing a smoother user experience.

**Technology Stack Used:**

* **Programming Languages:** Python 3.13, JavaScript (ES6+)
* **Framework:** Flask 3.1.2
* **Database:** SQLite
* **Testing Framework:** Pytest

---

## Testing & Debugging

I created and executed automated tests to verify correctness and reliability.

### 1. Running Tests

After activating the virtual environment, tests can be executed using:

```bash
pytest
# or
pytest -v
```

### 2. Test Coverage

* **Unit Tests:** I tested individual API endpoints (for example, ensuring destination creation returns HTTP 201).
* **Integration Tests:** I validated full workflows from frontend payloads through API endpoints to database persistence.
* **Business Logic Tests:** I specifically tested the double‑booking prevention logic to ensure venues cannot be booked more than once for the same date.

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd eternaal
```

### 2. Virtual Environment Setup

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Initialization

The application automatically creates the database if it does not exist. To reset it manually, I used:

```bash
python -c "from eternaal import create_app; from eternaal.db import init_db; app = create_app(); app.app_context().push(); init_db()"
```

*(This command clears existing data.)*

### 5. Run the Application

```bash
flask run
# or
python app.py
```

The application runs at `http://127.0.0.1:5000`.

### 6. Admin Login Credentials

* **Username:** admin
* **Password:** admin123

---

## Attributions & Resources

During development, I referred to the following resources:

* **Flask Documentation:** For the Application Factory pattern and Blueprint structure.
* **Bootstrap 5 Documentation:** For responsive layout and UI components such as cards and modals.
* **SQLite Documentation:** For database design and queries.
* **Google Fonts:** Used Playfair Display and Lato for typography.

---

## Generative AI Declaration

**AI‑Assisted Idea Generation and Structuring (Level 2/3)**

I used generative AI tools to support development in the following ways:

* Debugging specific errors (e.g., "Unsupported Media Type" issues in Fetch API calls).
* Refactoring the project structure into a modular Blueprint‑based Flask application.
* Generating boilerplate unit test structures and pytest fixtures.

All AI‑generated suggestions were critically reviewed, tested, and manually integrated by me. Core business logic, including availability checking and role‑based access control, was implemented and verified to meet the project requirements.

---

*Date: 14 December 2025*


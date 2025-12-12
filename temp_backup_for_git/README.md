# EternalVista - Destination Wedding Management System

EternalVista is a web application designed to help couples plan their dream destination weddings in Ireland. It features a simplified two-role system (Admin and Customer) and a comprehensive booking workflow.

## Features

### 1. User Roles
- **Admin**:
  - **Dashboard**: View analytics (Requests Today, Monthly Profit, Customer counts).
  - **Platform Settings**: Full CRUD (Create, Read, Update, Delete) control over **Destinations** and **Categories**.
  - **Booking Management**: View pending booking requests and Accept or Reject them.
- **Customer**:
  - **Registration/Login**: Dedicated signup flow.
  - **Search**: Interactive search on the landing page to find Services (e.g., Photography, Venues) in specific Destinations (e.g., Dublin, Wicklow).
  - **Booking**: Request bookings for specific dates and hours. Pricing is automatically calculated (default €100/hr).
  - **Dashboard**: View own bookings. Pay for bookings once they are accepted by the Admin.

### 2. Booking Workflow
1. **Search**: Customer searches for a service/destination on the Home page.
2. **Request**: Customer clicks "Book Now", selects Date/Hours -> Status: **Pending**.
3. **Approval**: Admin reviews request on Dashboard -> **Accepted** or **Rejected**.
4. **Payment**: Customer sees "Pay Now" button on Dashboard (if Accepted) -> Status: **Paid**.

### 3. Technical Highlights
- **Backend**: Python Flask with SQLite.
- **Frontend**: HTML5, Bootstrap 5, Vanilla JavaScript (fetch API for backend communication).
- **Design**: Premium "Gold & Dark" aesthetic using Google Fonts (Playfair Display).
- **Security**: Password hashing with Werkzeug, Session-based authentication.

## Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python app.py
   ```
   *The database (`database.db`) will be automatically created and seeded with initial data (Admin user, destinations, categories) on the first run.*

3. **Access the App**:
   - Open browser to: `http://127.0.0.1:5000`

## Default Credentials

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin` | `admin123` |
| **Customer** | `customer` | `customer123` |

## Project Structure
- `app.py`: Main Flask application.
- `instance/`: Contains `database.db` (Official location for data).
- `templates/`: HTML templates (Jinja2).
  - `admin/`: Admin Dashboard.
  - `user/`: Customer Dashboard & Booking Tables.
  - `auth/`: Login & Register.
  - `index.html`: Home Page.
  - `base.html`: Shared Layout.
- `static/`: CSS and Images.
- `tests/`: Simple tests for assignment requirements.

## Testing
To run the automated tests (as per assignment requirement):
```bash
python -m pytest
```

## Future Improvements
- Email notifications for booking status changes.
- Integration with a real payment gateway (Stripe/PayPal).
- User profile management.

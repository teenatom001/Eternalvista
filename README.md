Eternal – Destination Wedding System
Overview

Eternal is a web-based system for a boutique wedding planning agency in Ireland. It helps manage venues, destinations, and bookings efficiently, replacing manual spreadsheets and phone-based coordination. Customers can browse venues and make bookings, while admins can manage all data securely.

Technologies Used

Backend: Python 3.13, Flask 3.1.2

Frontend: HTML5, Bootstrap 5, JavaScript 

Database: SQLite

Testing: Pytest

Version Control: Git, GitHub

Features

Role-based Access: Admin (full access), Customer (limited access)

CRUD Operations: Create, Read, Update, Delete for Destinations, Venues, Bookings, and Users

Availability Checks: Prevents double booking

Validation: Ensures correct input in all forms

API-driven: Frontend fetches data via backend APIs asynchronously for a smooth user experience

References / Links

GitHub Repository: https://github.com/teenatom001/Eternalvista

Flask Documentation: https://flask.palletsprojects.com/

Bootstrap Documentation: https://getbootstrap.com/docs/5.0/getting-started/introduction/

Useful Commands


Setup & Run Project:

Create virtual environment

python -m venv venv

Activate environment (Windows)

venv\Scripts\activate


 Install dependencies
pip install -r requirements.txt

 Run the Flask app
flask run



Conclusion

The Eternal system provides an efficient, web-based solution for managing destination weddings. It replaces manual processes with a secure, user-friendly platform that supports role-based access, CRUD operations, and real-time availability checks. By centralizing venue, booking, and user management, the system reduces errors, saves time, and improves the overall experience for both customers and administrators.


References

chatgpt::https://chatgpt.com/c/693ff246-7bb4-8326-8374-a130a65c70d4,
https://chatgpt.com/c/693db122-5ad4-8333-9b88-f20ba34093c7
flask documentation:https://flask.palletsprojects.com/en/stable/tutorial/database/
flask-mega-tutorial:https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
youtubelink:https://youtu.be/SSqvwa2bx5k?si=DueQOFmAcLX_0Fin 
mozilla org:https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch

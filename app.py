from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash, g
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os
from datetime import datetime

# Initialize the Flask application
app = Flask(__name__)
# The secret key is used to sign session cookies for security
app.secret_key = 'my_secret_key'  
# CORS allows the frontend to easily talk to the backend if needed
CORS(app)  

# Ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

DATABASE = os.path.join(app.instance_path, 'database.db')


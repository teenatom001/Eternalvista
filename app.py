from flask import Flask, render_template
from db import get_db_connection
from models import create_category_table
create_category_table()


app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello"

# Admin routes
@app.route('/index')
def index():
    return render_template('admin/index.html')

@app.route('/category')
def category():
    return render_template('admin/category.html')

@app.route('/country')
def country():
    return render_template('admin/country.html')

@app.route('/city')
def city():
    return render_template('admin/city.html')

@app.route('/county')
def county():
    return render_template('admin/county.html')


# Vendor routes
@app.route('/vendorhome')
def vendorhome():
    return render_template('vendor/vendorhome.html')


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route('/')
def hello_world():
   return 'Hello'

# admin side
@app.route('/index')
def index():
    return render_template('/admin/index.html')

@app.route('/category')
def category():
    return render_template('/admin/category.html')

@app.route('/country')
def country():
    return render_template('/admin/country.html')

@app.route('/city')
def city():
    return render_template('/admin/city.html')

@app.route('/county')
def county():
    return render_template('/admin/county.html')

# vendor side
@app.route('/vendorhome')
def vendorhome():
    return render_template('vendor/vendorhome.html')


if __name__ == '__main__':
   db.create_all()  
   app.run(debug=True)
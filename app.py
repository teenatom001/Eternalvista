from flask import Flask, render_template,request,run_query
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

def add_category():
    if request.method == 'POST':
        category = request.form['category_name']
        image = request.form['image']

        success = run_query(
            "INSERT INTO category (category, image) VALUES (%s, %s)",
            (category, image)
        )

        if success:
            return "Inserted Successfully!"
        else:
            return "Category Not Inserted!"

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

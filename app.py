from flask import Flask, render_template, request
# from db import get_db_connection
# from models import create_category_table

# create_category_table()  # Creates table on start

app = Flask(__name__)




@app.route('/')
def hello():
    return "Hello"
@app.route('/admin/index')
def index():
    return render_template('admin/index.html')

@app.route('/category')
def category():
    return render_template('admin/category.html')


# @app.route('/add_category', methods=['POST'])
# def add_category():
#     category = request.form['category_name']
#     image = request.form['image']

#     success = run_query(
#         "INSERT INTO category (category, image) VALUES (%s, %s)",
#         (category, image)
#     )

#     if success:
#         return "Inserted Successfully!"
#     else:
#         return "Category Not Inserted!"


# Other admin pages
@app.route('/country')
def country():
    return render_template('admin/country.html')


@app.route('/city')
def city():
    return render_template('admin/city.html')


@app.route('/county')
def county():
    return render_template('admin/county.html')


@app.route('/vendorhome')
def vendorhome():
    return render_template('vendor/vendorhome.html')


if __name__ == '__main__':
    app.run(debug=True)

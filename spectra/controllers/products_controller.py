from spectra import app
from spectra.models import db
from spectra.models.product import Product
from spectra.controllers.user_helpers import check_user_validity
from flask import render_template, redirect, url_for, request, flash

@app.route("/")
def products_index():
    (valid, error) = check_user_validity()
    if not valid:
        flash(error)
        return redirect(url_for('login'))

    products = Product.query.all()
    return render_template("products/index.html", products=products)
    
#
# Show a product
#

@app.route("/products/<int:id>")
def show_product(id):
    product = Product.query.get_or_404(id)
    return render_template("products/show.html", product=product)

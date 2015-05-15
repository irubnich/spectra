from spectra import app
from spectra.models import db
from spectra.models.product import Product
from spectra.models.order_product import OrderProduct
from spectra.controllers.user_helpers import check_user_validity
from flask import render_template, redirect, url_for, request, flash, session

@app.before_request
def init_cart():
    if not session.has_key("cart"):
        session["cart"] = {
            "items": []
        }

@app.route("/")
def products_index():
    (valid, error) = check_user_validity()
    if not valid:
        flash(error)
        return redirect(url_for('login'))

    if (session["user"]["type"] == 'director'):
        return redirect(url_for('director_dashboard'))

    if (session["user"]["type"] == 'manager'):
        return redirect(url_for('manager_dashboard'))

    if (session["user"]["type"] == 'salesperson'):
        return redirect(url_for('salesperson_dashboard'))

    categories = db.session.query(Product.category.distinct()).all()
    category = request.args.get('category')
    if category:
        products = Product.query.filter_by(category=category).all()
    else:
        products = Product.query.all()

    if category:
        result = db.engine.execute("SELECT product_id, SUM(quantity) FROM order_products GROUP BY product_id ORDER BY SUM(quantity) DESC LIMIT 3;")

    return render_template("products/index.html", categories=categories, products=products, result=result)


#
# Show a product
#

@app.route("/products/<int:id>")
def show_product(id):
    (valid, error) = check_user_validity()
    if not valid:
        flash(error)
        return redirect(url_for('login'))

    product = Product.query.get_or_404(id)
    return render_template("products/show.html", product=product)

@app.route("/products/<int:id>/add-to-cart/<int:quantity>", methods=["POST"])
def add_to_cart(id, quantity):
    (valid, error) = check_user_validity()
    if not valid:
        flash(error)
        return redirect(url_for('login'))

    product = Product.query.get_or_404(id)
    quantity = request.form["quantity"]

    item_updated = False
    for item in session["cart"]["items"]:
        if item["product"] == product.id:
            print "FOUND"
            item["quantity"] = int(item["quantity"]) + int(quantity)
            item_updated = True
            break

    if not item_updated:
        session["cart"]["items"].append({
            "product": id,
            "quantity": quantity
        })
    flash("Successfully added {0} to cart.".format(product.name))

    if request.args.get('return_to_home'):
        return redirect(url_for("products_index"))

    return redirect(url_for("show_product", id=product.id))

from spectra import app
from spectra.models import db
from spectra.models.product import Product
from spectra.controllers.user_helpers import check_user_validity
from flask import render_template, redirect, url_for, request, flash, session
from IPython import embed


@app.route("/cart")
def cart_index():
    cart_items = session["cart"]["items"]
    products = []
    total = 0.0

    # loop over products currently in cart
    for cart_item in cart_items:
        db_product = Product.query.get(cart_item["product"])
        products.append({
            "product": db_product,
            "quantity": cart_item["quantity"]
        })
        total += (db_product.price * int(cart_item["quantity"]))

    return render_template('cart/index.html', products=products, total=total)

#
# Edit cart item quantity
#

@app.route("/cart", methods=["POST"])
def cart_edit():
    product_id = request.form["product_id"]
    quantity = request.form["quantity"]

    # product_dict = None
    for item in session["cart"]["items"]:
        if item["product"] == int(product_id):
            item["quantity"] = quantity
            break

    return redirect(url_for("cart_index"))

#
# Delete a cart item
#

@app.route("/cart/<int:id>/delete")
def cart_delete(id):
    product_dict = None
    for item in session["cart"]["items"]:
        if item["product"] == id:
            product_dict = item
            break

    session["cart"]["items"].remove(product_dict)
    return redirect(url_for('cart_index'))

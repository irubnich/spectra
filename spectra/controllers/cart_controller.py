from spectra import app
from spectra.models import db
from spectra.models.product import Product
from spectra.models.user import User
from spectra.controllers.user_helpers import check_user_validity
from flask import render_template, redirect, url_for, request, flash, session
from IPython import embed


@app.route("/cart")
def cart_index():
    (valid, error) = check_user_validity()
    if not valid:
        flash(error)
        return redirect(url_for('login'))

    cart_items = session["cart"]["items"]
    products = []
    subtotal = 0.0

    # loop over products currently in cart
    for cart_item in cart_items:
        db_product = Product.query.get(cart_item["product"])
        products.append({
            "product": db_product,
            "quantity": cart_item["quantity"],
			"inventory": db_product.inventory
        })
        subtotal += (db_product.price * int(cart_item["quantity"]))

    # Calculate discount
    user = User.query.get(session["user"]["id"])
    discount = (subtotal * user.discount)
    total = subtotal - discount

    return render_template('cart/index.html', products=products, subtotal=subtotal, discount=discount, total=total)

#
# Edit cart item quantity
#

@app.route("/cart", methods=["POST"])
def cart_edit():
    (valid, error) = check_user_validity()
    if not valid:
        flash(error)
        return redirect(url_for('login'))

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
    (valid, error) = check_user_validity()
    if not valid:
        flash(error)
        return redirect(url_for('login'))
        
    product_dict = None
    for item in session["cart"]["items"]:
        if item["product"] == id:
            product_dict = item
            break

    session["cart"]["items"].remove(product_dict)
    return redirect(url_for('cart_index'))

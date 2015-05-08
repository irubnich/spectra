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

    # loop over products currently in cart 
    for cart_item in cart_items:
        products.append({
            "product": Product.query.get(cart_item["product"]),
            "quantity": cart_item["quantity"]
        })
        
    return render_template('cart/index.html', products=products)

@app.route("/cart", methods=["POST"])
def cart_edit():
    quantity = request.form["quantity"]

    session["cart"]["items"].append({
        "product": id,
        "quantity": quantity
    })
    return redirect(url_for("cart_index"))













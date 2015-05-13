from spectra import app
from spectra.models import db
from spectra.models.rating import Rating
from spectra.models.order import Order
from spectra.models.user import User
from spectra.controllers.user_helpers import check_user_validity
from flask import render_template, redirect, url_for, request, flash, session
from IPython import embed
from datetime import datetime

# displays rating page, which displays orders that you completed but have not rated the user
@app.route("/ratings")
def rating_index():
    (valid, error) = check_user_validity()
    if not valid:
        flash(error)
        return redirect(url_for('login'))

    # Get all orders relevant to the current user
    user = User.query.get(session["user"]["id"])
    if user.type == "client":
        orders = Order.query.filter(Order.client_id == user.id).all()
    elif user.type == "salesperson":
        orders = Order.query.filter(Order.salesperson_id == user.id).all()

    # Further filter orders based on if the current user rated them
    orders = [i for i in orders if not i.is_rated_by_user(session["user"]["id"])]

    return render_template("ratings/index.html", orders=orders, user_type=user.type)

@app.route("/ratings/<int:order_id>/rate")
def rate(order_id):
    # Can we rate this order?
    order = Order.query.get(order_id)
    if order.is_rated_by_user(session["user"]["id"]):
        flash("You can't rate an order that you've already rated.")
        return redirect(url_for('products_index'))

    return render_template("ratings/rate.html", order_id=order_id)

@app.route("/ratings" , methods=["POST"])
def place_rating():
    user = User.query.get(session["user"]["id"])
    order_id = request.form["order_id"] # "order_id" is from the form
    order = Order.query.get(order_id)

    # Last check for if we can rate this order
    if order.is_rated_by_user(session["user"]["id"]):
        flash("You can't rate an order that you've already rated.")
        return redirect(url_for('products_index'))

    if user.type == "client":
        user_being_rated = order.salesperson_id
    elif user.type == "salesperson":
        user_being_rated = order.client_id

    rating_type = request.form["rating_type"]
    if rating_type == "1":
        rating_type = True
    else:
        rating_type = False

    score = user.rate(user_being_rated, user.id, order_id, rating_type)
    flash("Thank you for rating!")
    return redirect(url_for('products_index'))

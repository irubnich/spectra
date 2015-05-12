from spectra import app
from spectra.models import db
from spectra.models.user import User
from spectra.models.product import Product
from spectra.models.salespeople_client import SalespeopleClient
from spectra.models.order import Order
from spectra.models.order_product import OrderProduct
from spectra.controllers.user_helpers import check_user_validity
from spectra.models.salespeople_client import SalespeopleClient
from flask import render_template, redirect, url_for, request, flash, session
from datetime import datetime

@app.route("/checkout")
def checkout_page():
	(valid, error) = check_user_validity()
	if not valid:
		flash(error)
		return redirect(url_for('login'))

	cart_items = session["cart"]["items"]

	if len(cart_items) == 0:
		flash("You have no items in your cart!")
		return redirect(url_for('products_index'))

	products = []
	total = 0.0

	# Make cookie into list of products to display
	for cart_item in cart_items:
		db_product = Product.query.get(cart_item["product"])
		products.append({
			"product": db_product,
			"quantity": cart_item["quantity"]
		})
		total += (db_product.price * int(cart_item["quantity"]))

	return render_template("checkout/index.html", products=products, total=total)

@app.route("/checkout", methods=["POST"])
def place_order():
	user = User.query.get(session["user"]["id"])
	salesperson = user.get_salesperson()
	date = datetime.now()
	date_approved = None
	date_rejected = None

	# Build order from cookie
	# and confirm inventory
	products = session["cart"]["items"] # list of dictionaries
	total = 0
	for item in products:
		db_product = Product.query.get(item["product"])
		quantity = int(item["quantity"])

		if db_product.inventory < quantity:
			flash("There is not enough inventory remaining for {0}!".format(db_product.name))
			return redirect(url_for("cart_index"))

		total += (db_product.price * quantity)

	discount = user.discount
	user.discount = 0 #Discounts are one time use

	order = Order(user.id, salesperson.id, date, date_approved, date_rejected, total, discount)
	db.session.add(order)
	db.session.commit()

	for item in products:
		db_product = Product.query.get(item["product"])
		quantity = int(item["quantity"])

		# Decrement inventory
		db_product.inventory -= quantity

		# Commit order product
		order_product = OrderProduct(order.id, db_product.id, quantity)
		db.session.add(order_product)

	db.session.commit()

	# Clear cart!
	session["cart"]["items"] = []

	return redirect(url_for('order_confirm', id=order.id))

@app.route("/checkout/confirm/<int:id>")
def order_confirm(id):
	order = Order.query.get(id) #Obtain Order of the order id to find salesperson id
	salesperson = User.query.get(order.salesperson_id) #Obtain Salesperson so we can use his name

	order_items = OrderProduct.query.filter(OrderProduct.order_id == id).all() # = Select all products from OrderProduct in recent order so we can list them
	grouped_products = map(lambda item: { "product": Product.query.get(item.product_id), "quantity": item.quantity }, order_items)

	return render_template("checkout/confirm.html", products=grouped_products, total=order.total, salesperson=salesperson.name())

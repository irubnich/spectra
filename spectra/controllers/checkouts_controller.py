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

@app.route("/checkout")	#website todo and need to add how to get to this page
def checkout_page():
	(valid, error) = check_user_validity()
	if not valid:
		flash(error)
		return redirect(url_for('login'))

	cart_items = session["cart"]["items"]
	products = []
	total = 0.0

	# Make cookie into something coherent
	for cart_item in cart_items:
		db_product = Product.query.get(cart_item["product"])
		products.append({
			"product": db_product,
			"quantity": cart_item["quantity"]
		})
		total += (db_product.price * int(cart_item["quantity"]))

	return render_template("checkout/index.html", products=products, total=total)

@app.route("/checkout", methods=["POST"])	#todo and comes from a form page?
def place_order():
	user = User.query.get(session["user"]["id"])
	client_id = user.id
	salespeopleclient = SalespeopleClient.query.filter(SalespeopleClient.client_id == client_id).first()
	salesperson_id = salespeopleclient.salesperson_id
	date = datetime.now()
	date_approved = None
	date_rejected = None

	#might be wrong need checking
	products = session["cart"]["items"] # array of dictionaries
	total = 0
	for item in products:
		db_product = Product.query.get(item["product"])
		total += (db_product.price * int(item["quantity"]))

	discount = user.discount
	user.discount = 0 #Discounts are one time use

	order = Order(client_id, salesperson_id, date, date_approved, date_rejected, total, discount)
	db.session.add(order)
	db.session.commit()

	#order_product table might be wrong
	for item in products:
		db_product = Product.query.get(item["product"])
		db_quantity = item["quantity"]
		order_product = OrderProduct(order.id, db_product.id, db_quantity)
		db.session.add(order_product)

	db.session.commit()
	return redirect(url_for('order_confirm', id=order.id))

@app.route("/checkout/confirm/<int:id>")
def order_confirm(id):
	order = Order.query.filter(Order.id == id).first() #Obtain Order of the order id to find salesperson id
	salesperson = User.query.filter(User.id == order.salesperson_id).first() #Obtain Salesperson so we can use his name

	order_items = OrderProduct.query.filter(OrderProduct.order_id == id).all() # = Select all products from OrderProduct in recent order so we can list them

	grouped_products = map(lambda item: { "product": Product.query.get(item.product_id), "quantity": item.quantity }, order_items)

	return render_template("checkout/confirm.html", products=grouped_products, total=order.total, salesperson=salesperson.name())

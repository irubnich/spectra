from spectra import app
from spectra.models import db
from spectra.models.user import User
from spectra.models.product import Product
from spectra.models.product_suggestion import ProductSuggestion
from spectra.controllers.user_helpers import check_user_validity
from flask import render_template, redirect, url_for, request, flash, session

#Product Management Homepage
@app.route("/product_management")
def product_management_index():

    if (session["user"]["type"] == 'client'): 		## Clients cannot access product management
        flash("You don't have permission to access that page.")
        return redirect(url_for('index'))
		
    return render_template("product_management/index.html")
	
@app.route("/product_management/product_suggestion.html")
def suggest_product():
    if (session["user"]["type"] != 'salesperson'): 		## Only Salesperson can suggest a product
        flash("You don't have permission to access that page.")
        return redirect(url_for('index'))
		
    return render_template("product_management/product_suggestion.html")
	
@app.route("/product_management", methods=["POST"])
def place_suggestion():
	user = User.query.get(session["user"]["id"])
	name = request.form["name"]
	reason = request.form["reason"]	
	
	suggestion = ProductSuggestion(user.id, name, reason)
	db.session.add(suggestion)
	db.session.commit()
 
	return render_template("product_management/index.html")

@app.route("/product_management/new_product.html")
def create_product():
	if (session["user"]["type"] != 'director'): 		## Only Director can create a product
		flash("You don't have permission to access that page.")
		return redirect(url_for('index'))
	suggestions = ProductSuggestion.query.all()
	return render_template("product_management/new_product.html", suggestions=suggestions)

@app.route("/product_management/new_product.html", methods=["POST"])
def confirm_product():
	user = User.query.get(session["user"]["id"])
	product_name = request.form["product_name"]
	description = request.form["reason"]
	
	product = Product(product_name, description, 9999999, "No Category", 0, 0.0, "")
	db.session.add(product)
	db.session.commit()
 
	return redirect(url_for('edit_product_page', id=product.id))

@app.route("/product_management/<int:id>/edit_product.html")
def edit_product_page(id):
	if ((session["user"]["type"] == 'client') or (session["user"]["type"] == 'salesperson')): 		## Only Director can create a product
		flash("You don't have permission to access that page.")
		return redirect(url_for('index'))
	product = Product.query.get(id)
	return render_template("product_management/edit.html", product=product, user_type=session["user"]["type"])

@app.route("/product_management/product_list.html")
def edit_product_list():
	if ((session["user"]["type"] == 'client') or (session["user"]["type"] == 'salesperson')): 		## Only Director can create a product
		flash("You don't have permission to access that page.")
		return redirect(url_for('index'))
	products = Product.query.all()

	return render_template("product_management/product_list.html", products=products, user_type=session["user"]["type"])

@app.route("/product_management/product_list.html", methods=["POST"])
def confirm_edit_product():
	product = Product.query.filter(Product.id == request.form["product_id"])
	if (session["user"]["type"] == 'director'):
		product.name = request.form["product_name"]
		product.description = request.form["description"]
		product.price = request.form["price"]
		product.category = request.form["category"]
		product.inventory = request.form["inventory"]
		product.promotion = request.form["promotion"]
		product.image = request.form["image"]
	elif (session["user"]["type"] == 'manager'):
		product.name = request.form["promotion"]		
	db.session.commit()
	return render_template("product_management/index.html")
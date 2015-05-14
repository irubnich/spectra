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
	#user = User.query.get(session["user"]["id"])
    product_name = request.form["product_name"]
    description = request.form["description"]
    price = request.form["price"]
    category = request.form["category"]
    inventory = request.form["inventory"]
    promotion = request.form["promotion"] 
    image_url = request.form["image_url"]

    # Validation

    required_fields = [product_name, description, price, category, inventory, promotion, image_url]
    trimmed = [i.strip() for i in required_fields]
    if "" in trimmed:
        flash("You're missing required fields.")
        return redirect(url_for('confirm_product'))

    try:
        price = float(price)
    except ValueError:
        flash("Invalid conversion for price")
        return redirect(url_for('confirm_product'))

    if price < 0:
        flash("Invalid entry for price")
        return redirect(url_for('confirm_product'))

    try:
        inventory = int(inventory)
    except ValueError:
        flash("Invalid conversion for inventory")
        return redirect(url_for('confirm_product'))

    if inventory < 0:
        flash("Invalid entry for inventory")
        return redirect(url_for('confirm_product'))

    try:
        promotion = float(promotion)
    except ValueError:
        flash("Invalid conversion for promotion")
        return redirect(url_for('confirm_product'))

    if promotion < 0:
        flash("Invalid entry for promotion")
        return redirect(url_for('confirm_product'))

    product = Product(product_name, description, price, category, inventory, promotion, image_url)
    db.session.add(product)
    db.session.commit()

    flash("Product created!")
    return redirect(url_for('product_management_index'))

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






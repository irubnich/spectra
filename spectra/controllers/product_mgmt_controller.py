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
    if (session["user"]["type"] != 'director'):             ## only director could delete users
        flash("You don't have permission to access that page.")
        return redirect(url_for('index'))
	return render_template("product_management/index.html")

@app.route("/product_management/product_suggestion")
def list_suggested_products():
    if (session["user"]["type"] != 'director'): 		## Only Director can create a product
        flash("You don't have permission to access that page.")
        return redirect(url_for('director_dashboard'))
    
    suggestions = ProductSuggestion.query.all()
    salespeople = User.query.all()

    return render_template("product_management/product_suggestion.html", suggestions=suggestions, salespeople=salespeople)

@app.route("/product_management/new_product", defaults={'id': None})
@app.route("/product_management/new_product/<int:id>")
def create_product(id):
    if (session["user"]["type"] != 'director'): 		## Only Director can create a product
        flash("You don't have permission to access that page.")
        return redirect(url_for('director_dashboard'))
    
    new_product_name = None
    if id:
        suggestion = ProductSuggestion.query.get_or_404(id)
        new_product_name = suggestion.name
        db.session.delete(suggestion)
        db.session.commit()
        
    return render_template("product_management/new_product.html", new_product_name=new_product_name)

@app.route("/product_management/reject_suggestion/<int:id>")
def reject_suggestion(id):
    if (session["user"]["type"] != 'director'): 		## Only Director can create a product
        flash("You don't have permission to access that page.")
        return redirect(url_for('director_dashboard'))
    
    suggestion = ProductSuggestion.query.get_or_404(id)
    db.session.delete(suggestion)
    db.session.commit()
    
    flash("Suggestion has been rejected.")
    return redirect(url_for('list_suggested_products'))
        

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

    if inventory < 1:
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

    product = Product(product_name, description, price, category, inventory, (promotion/100), image_url, 1)
    db.session.add(product)
    db.session.commit()

    flash("Product is created!")
    return redirect(url_for('director_dashboard'))


@app.route("/product_management/product_list.html")
def edit_product_list():
    if (session["user"]["type"] != 'director'):             ## only director could delete users
        flash("You don't have permission to access that page.")
        return redirect(url_for('director_dashboard'))
    
    products = Product.query.all()
    return render_template("product_management/product_list.html", products=products)

@app.route("/product_management/edit_product/<int:id>") 
def edit_product(id):
    if (session["user"]["type"] != 'director'):             ## only director could delete users
        flash("You don't have permission to access that page.")
        return redirect(url_for('director_dashboard'))
    
    products = Product.query.all()
    product = Product.query.get(id)
    return render_template("product_management/edit.html", product=product, products =products)


@app.route("/product_management/edit_product/<int:id>", methods=["POST"])
def confirm_edit_product(id):
    if (session["user"]["type"] != 'director'):             ## only director could delete users
        flash("You don't have permission to access that page.")
        return redirect(url_for('director_dashboard'))
    
    products = Product.query.all()
    product = Product.query.get(id)

    product.name = request.form["name"]
    product.description = request.form["description"]
    product.price = request.form["price"]
    product.category = request.form["category"]
    product.inventory = request.form["inventory"]
    promotion = request.form["promotion"]
    product.promotion = float(promotion)/100
    product.image = request.form["image"]
		
    db.session.commit()
    flash("Changes have been made to product.")
    
    return redirect(url_for('edit_product', id=product.id))

@app.route("/product_management/products_visibility")
def visible_product():
    if (session["user"]["type"] != 'director'):             ## only director could delete users
        flash("You don't have permission to access that page.")
        return redirect(url_for('director_dashboard'))
    
    products = Product.query.all()
    
    return render_template("product_management/products_visibility.html", products=products)    
    
@app.route("/product_management/products_visibility", methods=["POST"])
def confirm_visible_product():
    if (session["user"]["type"] != 'director'): 		## Only Director can create a product
        flash("You don't have permission to access that page.")
        return redirect(url_for('director_dashboard'))
    
    products = Product.query.all()
    checked = request.form.getlist("checked")
    for product_id in checked:
        product = Product.query.get(product_id)
        if (product.active == 1):
            product.active = 0
        elif (product.active == 0):
            product.active = 1
    db.session.commit()
    flash("Changes have been made to products visibility.")
    return redirect(url_for('visible_product'))
    
    
    
@app.route("/product_management/delete_product/<int:id>")
def remove_product(id):

    if (session["user"]["type"] != 'director'):             ## only director could delete users
        flash("You don't have permission to access that page.")
        return redirect(url_for('director_dashboard'))
    
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash("Product has been removed.")
    return redirect(url_for('director_dashboard'))
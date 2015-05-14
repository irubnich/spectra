from spectra import app
from spectra.models import db
from spectra.models.user import User
from spectra.models.product import Product
from spectra.models.managers_salespeople import Manager_salespeople
from flask import render_template, redirect, url_for, request, flash, session
import re
import hashlib
from datetime import datetime

@app.route("/dashboards/director")
def director_dashboard():
    return render_template("dashboards/director.html")

#
# Manager Actions
#

@app.route("/dashboards/manager", defaults={'id': None})
@app.route("/dashboards/manager/<int:id>")
def manager_dashboard(id):
    user = User.query.get(session["user"]["id"])
    salespeople = sorted(user.get_salespeople(), key=lambda x: x.rating(), reverse=True)

    salesperson = None
    if id:
        salesperson = User.query.get(id)

    return render_template("dashboards/manager.html", salespeople=salespeople, salesperson=salesperson)

@app.route("/dashboards/manager/unsuspend/<int:id>")
def manager_unsuspend_salesperson(id):
    user = User.query.get(id)
    user.active = True
    db.session.commit()

    return redirect(url_for('manager_dashboard', id=user.id))

@app.route("/dashboards/manager/edit-commission/<int:id>")
def manager_edit_commission(id):
    pass

@app.route("/dashboards/manager/fire-salesperson/<int:id>")
def manager_fire_salesperson(id):
    user = User.query.get(id)
    db.session.delete(user)

    # Delete Manager_salespeople entry
    relation = Manager_salespeople.query.filter(Manager_salespeople.salesperson_id == id).first()
    db.session.delete(relation)

    db.session.commit()

    return redirect(url_for('manager_dashboard'))

@app.route("/dashboards/manager/hire")
def manager_hire_salesperson():
    return render_template("dashboards/manager/hire_salesperson.html")

@app.route("/dashboards/manager/hire", methods=["POST"])
def manager_hire_salesperson_process():
    email = request.form["email"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    init_password = request.form["password"]
    confirm_password = request.form["confirm_password"]

    # Validation
    required_fields = [email, first_name, last_name, init_password, confirm_password]
    trimmed = [i.strip() for i in required_fields]
    if "" in trimmed:
        flash("You're missing required fields.")
        return redirect(url_for('manager_hire_salesperson'))

    # Password matching
    if init_password != confirm_password:
        flash("Your passwords do not match.")
        return redirect(url_for('manager_hire_salesperson'))

    # Email validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        flash("Your email address is invalid.")
        return redirect(url_for('manager_hire_salesperson'))

    password = hashlib.sha512(init_password).hexdigest()

    date_created = datetime.now()

    user = User(email, "salesperson", first_name, last_name, password, True, date_created, 0.0, 0.0)
    db.session.add(user)
    db.session.commit()

    manager = User.query.get(session["user"]["id"])
    sales_mgr = Manager_salespeople(manager.id, user.id)
    db.session.add(sales_mgr)

    db.session.commit()

    flash("Hiring process is complete.")
    return redirect(url_for('manager_dashboard', id=user.id))

@app.route("/dashboards/manager/blacklist-client/<int:id>")
def manager_blacklist_client(id):
    user = User.query.get(id)
    user.active = False
    db.session.commit()

    flash("Client blacklisted.")
    return redirect(url_for('manager_dashboard', id=user.get_salesperson().id))

@app.route("/dashboards/manager/unblacklist-client/<int:id>")
def manager_unblacklist_client(id):
    user = User.query.get(id)
    user.active = True
    db.session.commit()

    flash("Client unblacklisted.")
    return redirect(url_for('manager_dashboard', id=user.get_salesperson().id))

@app.route("/dashboards/manager/set-product-promotion")
def manager_set_product_promotion():
    products = Product.query.all()
    return render_template("dashboards/manager/set_product_promotion.html", products=products)

@app.route("/dashboards/manager/set-product-promotion", methods=["POST"])
def manager_set_product_promotion_process():
    product = Product.query.get(request.form["product"])
    product.promotion = float(request.form["promotion"]) / 100
    db.session.commit()

    flash("Product promotion updated.")
    return redirect(url_for('manager_dashboard'))

@app.route("/dashboards/manager/set-salesperson-commission/<int:id>")
def manager_set_salesperson_commission(id):
    salesperson = User.query.get(id)
    return render_template("dashboards/manager/set_salesperson_commission.html", salesperson=salesperson)

@app.route("/dashboards/manager/set-salesperson-commission/<int:id>", methods=["POST"])
def manager_set_salesperson_commission_process(id):
    salesperson = User.query.get(id)
    salesperson.commission = float(request.form["commission"]) / 100
    db.session.commit()

    return redirect(url_for('manager_dashboard', id=salesperson.id))

#
# Salesperson Actions
#

@app.route("/dashboards/salesperson", defaults={'id': None})
@app.route("/dashboards/salesperson/<int:id>")
def salesperson_dashboard(id):
    user = User.query.get(session["user"]["id"])
    clients = user.get_clients()

    return render_template("dashboards/salesperson.html")

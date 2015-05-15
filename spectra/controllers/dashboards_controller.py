from spectra import app
from spectra.models import db
from spectra.models.user import User
from spectra.models.product import Product
from spectra.models.order import Order
from spectra.models.salespeople_client import SalespeopleClient
from spectra.models.invitation import Invitation
from spectra.models.product_suggestion import ProductSuggestion
from spectra.models.managers_salespeople import Manager_salespeople
from flask import render_template, redirect, url_for, request, flash, session
import random
import string
from datetime import datetime
import re
import hashlib

@app.route("/dashboards/director", defaults={'id': None})
@app.route("/dashboards/director/<int:id>")
def director_dashboard(id):
    managers = sorted(User.query.filter(User.type == 'manager').all(), key=lambda x: x.rating(), reverse=True)
    rating = None
    manager = None
    if id:
        manager = User.query.get(id)
        salespeople = sorted(manager.get_salespeople(), key=lambda x: x.rating(), reverse=True)

        if len(salespeople) != 0:
            sum_ratings = 0.0
            for sp in salespeople:
                sum_ratings += sp.rating()
            rating = sum_ratings / len(salespeople)
        else:
            rating = 0.0

    return render_template("dashboards/director.html", managers=managers, manager=manager, rating=rating)

#
# Director Actions
#

@app.route("/dashboards/hire", methods=["GET"])
def hire():
    managers = User.query.filter(User.type == 'manager').all()
    return render_template("dashboards/hire.html", managers=managers)

@app.route("/dashboards/hire", methods=["POST"])
def new_employee():
    if (session["user"]["type"] != 'director'):             ## only director could delete users
        flash("You don't have permission to access that page.")
        return redirect(url_for('director_dashboard'))

    position_applied = request.form["position"]
    assigned_manager = request.form["ass_manager"]
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
        return redirect(url_for('hire'))

    # Password matching
    if init_password != confirm_password:
        flash("Your passwords do not match.")
        return redirect(url_for('hire'))

    # Email validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        flash("Your email address is invalid.")
        return redirect(url_for('hire'))

    password = hashlib.sha512(init_password).hexdigest()

    date_created = datetime.now()

    # Salesperson Managers relationship validation
    if (position_applied == 'manager' and assigned_manager != ""):
        flash("Select Assigned Manager as 'Nothing Selected' if you are hiring a manager.")
        return redirect(url_for('hire'))

    # Salesperson Managers relationship validation
    if (position_applied == 'salesperson' and assigned_manager == ""):
        flash("You have to Select assigned Manager.")
        return redirect(url_for('hire'))

    user = User(email, position_applied, first_name, last_name, password, True, date_created, 0.0, 0.0)
    db.session.add(user)
    db.session.commit()

    if (position_applied == 'salesperson'):
        manager = User.query.get(assigned_manager)
        if manager.type != "manager":
            raise BaseException("Can't assign a non-manager as a manager...")

        sales_mgr = Manager_salespeople(manager.id, user.id)
        db.session.add(sales_mgr)
        db.session.commit()

    flash("Hiring process is complete.")
    return redirect(url_for('director_dashboard'))

#
# Fire/Delete a User
#

@app.route("/dashboards/fire/<int:id>")
def fire(id):
    if (session["user"]["type"] != 'director'):             ## only director could delete users
        flash("You don't have permission to access that page.")
        return redirect(url_for('director_dashboard'))

    user = User.query.get_or_404(id)
    db.session.delete(user)

    # Delete salesperson manager table
    if user.type == "salesperson":
        relation = Manager_salespeople.query.filter(Manager_salespeople.salesperson_id == id).first()
        db.session.delete(relation)

    db.session.commit()
    flash("Employee has been fired.")
    return redirect(url_for('director_dashboard'))

#
# Unsuspend a salesperson/manager
#

@app.route("/dashboards/unsuspend/<int:id>")
def unsuspend(id):

    if (session["user"]["type"] != 'director'):             ## only director could delete users
        flash("You don't have permission to access that page.")
        return redirect(url_for('director_dashboard'))

    user = User.query.get_or_404(id)

    if (user.active == 0):
        if (user.type == 'salesperson'):
            user.active = 1
            flash("Salesperson is now active.")
        elif (user.type == 'manager'):
            user.active = 1
            flash("Manager is now active.")
    db.session.commit()
    return redirect(url_for('director_dashboard', id=user.id))

#
# Promote/Demote a User
#

@app.route("/dashboards/promote_demote/<int:id>")
def promote_demote(id):

    if (session["user"]["type"] != 'director'):             ## only director could delete users
        flash("You don't have permission to access that page.")
        return redirect(url_for('director_dashboard'))

    user = User.query.get_or_404(id)

    if (user.type == 'salesperson'):
        user.type = 'manager'
        flash("Salesperson has been promoted to Manager.")
    elif (user.type == 'manager'):
        user.type = 'salesperson'
        flash("Manager has been demoted to Salesperson.")

    db.session.commit()
    return redirect(url_for('director_dashboard'))

#
# Blacklist/Unblacklist a User
#

@app.route("/dashboards/blacklist/<int:id>")
def blacklist(id):
    if (session["user"]["type"] != 'director'):             ## only director could delete users
        flash("You don't have permission to access that page.")
        return redirect(url_for('director_dashboard'))

    user = User.query.get_or_404(id)

    if (user.type == 'client' and user.active == 1):
        user.active = '0'
        flash("Client has been blacklisted.")
    elif (user.type == 'client' and user.active == 0):
        user.active = '1'
        flash("Client has been removed from the blacklist.")

    db.session.commit()
    return redirect(url_for('director_dashboard', id=user.id))

#
# Manager Actions
#

@app.route("/dashboards/manager", defaults={'id': None})
@app.route("/dashboards/manager/<int:id>")
def manager_dashboard(id):
    user = User.query.get(session["user"]["id"])
    salespeople = sorted(user.get_salespeople(), key=lambda x: x.rating(), reverse=True)

    if len(salespeople) != 0:
        sum_ratings = 0.0
        for sp in salespeople:
            sum_ratings += sp.rating()
        rating = sum_ratings / len(salespeople)
    else:
        rating = 0.0

    salesperson = None
    if id:
        salesperson = User.query.get(id)

    return render_template("dashboards/manager.html", salespeople=salespeople, salesperson=salesperson, rating=rating)

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

    client = None
    if id:
        client = User.query.get(id)

    if len(clients) != 0:
        sum_ratings = 0.0
        for sp in clients:
            sum_ratings += sp.rating()
        rating = sum_ratings / len(clients)
    else:
        rating = 0.0

    return render_template("dashboards/salesperson.html", clients=clients, client=client, rating=rating)

@app.route("/dashboards/salesperson/approve_order/<int:id>")
def salesperson_approve_order(id):
    order = Order.query.get(id)
    order.date_approved = datetime.now()
    db.session.commit()

    flash("Order accepted.")
    return redirect(url_for('salesperson_dashboard', id=order.client().id))

@app.route("/dashboards/salesperson/reject_order/<int:id>")
def salesperson_reject_order(id):
    order = Order.query.get(id)
    order.date_rejected = datetime.now()
    db.session.commit()

    flash("Order rejected.")
    return redirect(url_for('salesperson_dashboard', id=order.client().id))

@app.route("/dashboards/salesperson/suggest-product")
def salesperson_suggest_product():
    return render_template("dashboards/salesperson/suggest_product.html")

@app.route("/dashboards/salesperson/suggest-product", methods=["POST"])
def salesperson_suggest_product_process():
    suggestion = ProductSuggestion(session["user"]["id"], request.form["product_name"], request.form["reason"])
    db.session.add(suggestion)
    db.session.commit()

    flash("Successfully added product suggestion.")
    return redirect(url_for('salesperson_dashboard'))

@app.route("/dashboards/salesperson/invite-client")
def salesperson_invite_client():
    return render_template("dashboards/salesperson/invite_client.html")

@app.route("/dashboards/salesperson/invite-client", methods=["POST"])
def salesperson_invite_client_process():
    email = request.form["client_email"]
    date = datetime.now()
    code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(15))

    invite = Invitation(code, session["user"]["id"], email, date)
    db.session.add(invite)
    db.session.commit()

    flash("Client invited! The code is: {0}".format(code))
    return redirect(url_for('salesperson_dashboard'))

@app.route("/dashboards/salesperson/claim-client")
def salesperson_claim_client():
    clients = User.query.filter(User.type == "client").all()
    unclaimed_clients = []
    for client in clients:
        if not client.get_salesperson():
            unclaimed_clients.append(client)

    return render_template("dashboards/salesperson/claim_client.html", unclaimed_clients=unclaimed_clients)

@app.route("/dashboards/salesperson/claim-client/<int:id>")
def salesperson_claim_client_process(id):
    user = User.query.get(id)
    association = SalespeopleClient(session["user"]["id"], user.id)

    db.session.add(association)
    db.session.commit()

    flash("Client claimed.")
    return redirect(url_for('salesperson_dashboard', id=user.id))

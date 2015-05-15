from spectra import app
from spectra.models import db
from spectra.models.user import User
from spectra.models.product import Product
from spectra.models.managers_salespeople import Manager_salespeople
from flask import render_template, redirect, url_for, request, flash, session
import re
import hashlib
from datetime import datetime

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

from spectra import app
from spectra.models import db
from spectra.models.user import User
from spectra.models.invitation import Invitation
from spectra.models.salespeople_client import SalespeopleClient
from spectra.controllers.user_helpers import set_session
from flask import render_template, redirect, url_for, request, session, flash
from IPython import embed
from datetime import datetime
import hashlib
import re

#
# Login
#

@app.route("/login", methods=["GET"])
def login():
    return render_template("users/login.html")

@app.route("/login", methods=["POST"])
def process_login():
    email = request.form["email"]
    password = request.form["password"]

    # Validation
    required_fields = [email, password]
    trimmed = [i.strip() for i in required_fields]
    if "" in trimmed:
        flash("You're missing required fields.")
        return redirect(url_for('login'))

    # Email validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        flash("Your email address is invalid.")
        return redirect(url_for('login'))

    user = User.authenticate(email, password)
    if user:
        set_session(user)
        return redirect(url_for("products_index"))

    flash("Invalid login.")
    return redirect(url_for("login"))

#
# List Users
#

@app.route("/users")
def index():
    users = User.query.all() # = Select * from users
    return render_template("users/index.html", users=users)

#
# Show a User
#

@app.route("/users/<int:id>")
def show(id):
    user = User.query.get_or_404(id)
    return render_template("users/show.html", user=user)

#
# Create a User
#

@app.route("/users/new", methods=["GET"])
def new():
    return render_template("users/new.html")

@app.route("/users/new", methods=["POST"])
def create():
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
        return redirect(url_for('new'))

    # Password matching
    if init_password != confirm_password:
        flash("Your passwords do not match.")
        return redirect(url_for('new'))

    # Email validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        flash("Your email address is invalid.")
        return redirect(url_for('new'))

    password = hashlib.sha512(init_password).hexdigest()

    invite_code = request.form["invitation_code"]
    if invite_code:
        invite = Invitation.query.filter(Invitation.invite_code == invite_code).first()
        if not invite or invite.user_id:
            flash("Your invitation code is invalid.")
            return redirect(url_for('new'))

        salesperson = User.query.get(invite.salesperson_id)
        if not salesperson or not salesperson.active:
            flash("Your invitation code is for a salesperson who does not exist or is inactive.")
            return redirect(url_for('new'))

    date_created = datetime.now()

    user = User(email, "client", first_name, last_name, password, True, date_created)
    db.session.add(user)
    db.session.commit()

    # Associate client with salesperson
    if invite_code:
        association = SalespeopleClient(salesperson.id, user.id)
        db.session.add(association)

        # Update invite so it's used
        invite.user_id = user.id
        db.session.commit()
    else:
        flash("You have been signed up but you cannot access Spectra until you are claimed by a Salesperson.")
        return redirect(url_for('login'))

    # Login!
    set_session(user)
    return redirect(url_for('products_index'))

#
# Edit a User
#

@app.route("/users/<int:id>/edit")
def edit(id):
    user = User.query.get_or_404(id)
    return render_template("users/edit.html", user=user)

@app.route("/users/<int:id>/update", methods=['POST'])
def update(id):
    user = User.query.get_or_404(id)
    user.email = request.form["email"]
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('show', id=id))

#
# Delete a User
#

@app.route("/users/<int:id>/destroy")
def destroy(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('index'))

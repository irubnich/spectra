from spectra import app
from spectra.models import db
from spectra.models.user import User
from spectra.models.invitation import Invitation
from spectra.controllers.user_helpers import set_session
from flask import render_template, redirect, url_for, request, session
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
		return redirect(url_for('login', error="You're missing required fields"))

	# Email validation
	if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
		return redirect(url_for('login', error="Your email address is invalid."))

	user = User.authenticate(email, password)
	if user:
		set_session(user)
		return redirect(url_for("products_index"))
	return redirect(url_for("login", error="Invalid login."))

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
	type = "client"
	first_name = request.form["first_name"]
	last_name = request.form["last_name"]
	init_password = request.form["password"]
	confirm_password = request.form["confirm_password"]

	# Validation
	required_fields = [email, type, first_name, last_name, init_password, confirm_password]
	trimmed = [i.strip() for i in required_fields]
	if "" in trimmed:
		return redirect(url_for('new', error="You're missing required fields."))

	# Password matching
	if init_password != confirm_password:
		return redirect(url_for('new', error="Your passwords do not match."))

	# Email validation
	if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
		return redirect(url_for('new', error="Your email address is invalid."))

	password = hashlib.sha512(init_password).hexdigest()

	invite_code = request.form["invitation_code"]
	invite =  Invitation.query.filter(Invitation.invite_code == invite_code).first()
	if invite:
		# actually check the salespeople/clients table.
		active = "1"
	else:
		active = "0"

	date_created = datetime.now()
	user = User(email,type,first_name,last_name, password, active, date_created)
	db.session.add(user)
	db.session.commit()

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

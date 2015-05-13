from spectra import app
from spectra.models import db
from spectra.models.user import User
from spectra.controllers.user_helpers import check_user_validity
from flask import render_template, redirect, url_for, request, flash, session


#
# Hire a User
#

@app.route("/users/hire")
def hire():

    if (session["user"]["type"] != 'director'):             ## only director could delete users
        flash("You don't have permission to access that page.")
        return redirect(url_for('index'))
    return render_template("users/hire.html")

@app.route("/users/hire", methods=["POST"])
def new_employee():
    email = request.form["email"]
    position = request.form["position"]
    confirm_code = request.form["confirm_code"]

    # Validation
    required_fields = [email, first_name, last_name, init_password, confirm_password]
    trimmed = [i.strip() for i in required_fields]
    if "" in trimmed:
        flash("You're missing required fields.")
        return redirect(url_for('hire'))

    # Email validation
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        flash("Your email address is invalid.")
        return redirect(url_for('new'))

    flash("A new employee will be notified to complete the process!")
    return redirect(url_for('index'))

@app.route("/users/new_hire")
def create_employee():
    
    position_applied = request.form["email"]
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

    user = User(email, "", first_name, last_name, password, True, date_created, 0.0, 0.0)
    db.session.add(user)
    db.session.commit()


    # Login!
    set_session(user)
    flash("Welcome to Spectra!")
    return redirect(url_for('products_index'))
    
#
# Delete a User
#

@app.route("/users")
def fire(id):

    if (session["user"]["type"] != 'director'):             ## only director could delete users
        flash("You don't have permission to access that page.")
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('index'))

#
# Show a User
#
 
@app.route("/users/<int:id>")
def show(id):
    
    if (session["user"]["type"] != 'director'):             ## only director could delete users
        flash("You don't have permission to access that page.")
        return redirect(url_for('index'))
    
    
    user = User.query.get_or_404(id)
    return render_template("users/show.html", user=user)


#
# (un)Blacklist a User 
#
 
@app.route("/users", methods=["post"])
def blacklist(id):
    
    if (session["user"]["type"] != 'director'):             ## only director could delete users
        flash("You don't have permission to access that page.")
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(id)
    
    if (user.active == '1'):
        user.active = '0'
        db.session.add(user)
        db.session.commit()
        flash("Client has been blacklisted.")
        return redirect(url_for('index')) 
    else:
        user.active = '1'
        db.session.add(user)
        db.session.commit()
        flash("Client has been removed from the blacklist.")
        return redirect(url_for('index'))
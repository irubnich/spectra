from spectra import app
from spectra.models import db
from spectra.models.user import User
from spectra.models.complaint import Complaint
from spectra.models.salespeople_client import SalespeopleClient
from spectra.controllers.user_helpers import check_user_validity
from flask import render_template, redirect, url_for, request, session, flash
from IPython import embed
from datetime import datetime

@app.route("/complaints/new")
def new_complaint():
    (valid, error) = check_user_validity()
    if not valid:
        flash(error)
        return redirect(url_for('login'))

    user = User.query.get(session["user"]["id"])
    clients = None
    if user.type == "salesperson":
        clients = user.get_clients()

    return render_template("complaints/new.html", clients=clients)

@app.route("/complaints/new", methods=["POST"])
def create_complaint():
    (valid, error) = check_user_validity()
    if not valid:
        flash(error)
        return redirect(url_for('login'))

    details = request.form["details"]

    # Validation
    required_fields = [details]
    trimmed = [i.strip() for i in required_fields]
    if "" in trimmed:
        flash("You're missing required fields.")
        return redirect(url_for('new_complaint'))

    complainer = User.query.get(session["user"]["id"])

    if complainer.type == "client":
        other_user = complainer.get_salesperson()
        num_prev_complaints = len(other_user.complaints().all()) + 1 # Adding one for the current complaint

        # Suspend?
        if num_prev_complaints % 9 == 0 and num_prev_complaints > 0:
            print "Suspending {0}!".format(other_user.email)
            other_user.suspend()

        # Commission decrease? Make sure we they are not suspended, that's punishment enough...
        if num_prev_complaints % 2 == 0 and num_prev_complaints > 0 and other_user.active:
            print "Decreasing commission for {0}!".format(other_user.email)
            other_user.commission = other_user.commission * 0.9
            db.session.commit()

    if complainer.type == "salesperson":
        other_user = User.query.get(request.form["client"])

        # Blacklist?
        num_prev_complaints = len(other_user.complaints().all()) + 1 # Adding one for the current complaint
        if num_prev_complaints % 2 == 0 and num_prev_complaints > 0:
            print "Blacklisting {0}!".format(other_user.email)
            other_user.blacklist()

    complaint = Complaint(other_user.id, complainer.id, details, datetime.now())
    db.session.add(complaint)
    db.session.commit()

    flash("You have successfully complained against {0}".format(other_user.name()))
    return redirect(url_for("products_index"))

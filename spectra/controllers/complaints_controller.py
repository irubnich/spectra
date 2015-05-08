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
        relations = SalespeopleClient.query.filter(SalespeopleClient.salesperson_id == user.id)
        clients = map(lambda relation: User.query.get(relation.client_id), relations)

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

    if complainer.type == "salesperson":
        other_user = User.query.get(request.form["client"])

        # Blacklist?
        num_prev_complaints = len(other_user.complaints().all())
        if num_prev_complaints % 2 == 0 and num_prev_complaints > 0:
            other_user.active = false

    complaint = Complaint(other_user.id, complainer.id, details, datetime.now())
    db.session.add(complaint)
    db.session.commit()

    flash("You have successfully complained against {0}".format(other_user.name()))
    return redirect(url_for("products_index"))

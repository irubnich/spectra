from spectra import app
from spectra.models.user import User
from flask import render_template, redirect, url_for, request, flash, session

@app.route("/dashboards/director")
def director_dashboard():
    return render_template("dashboards/director.html")

@app.route("/dashboards/manager", defaults={'id': None})
@app.route("/dashboards/manager/<int:id>")
def manager_dashboard(id):
    user = User.query.get(session["user"]["id"])
    salespeople = sorted(user.get_salespeople(), key=lambda x: x.rating(), reverse=True)

    salesperson = None
    if id:
        salesperson = User.query.get(id)

    return render_template("dashboards/manager.html", salespeople=salespeople, salesperson=salesperson)

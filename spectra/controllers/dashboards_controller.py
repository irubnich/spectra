from spectra import app
from flask import render_template, redirect, url_for, request, flash, session

@app.route("/dashboards/director")
def director_dashboard():
    return render_template("dashboards/director.html")

@app.route("/dashboards/manager")
def manager_dashboard():
    return render_template("dashboards/manager.html")

from spectra import app
from spectra.models import db
from spectra.controllers.user_helpers import is_logged_in
from flask import render_template, redirect, url_for, request
from IPython import embed

@app.route("/")
def products_index():
    if is_logged_in():
        return render_template("products/index.html")
    else:
        return redirect(url_for('login'))

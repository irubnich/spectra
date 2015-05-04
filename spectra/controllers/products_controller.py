from spectra import app
from spectra.models import db
from spectra.controllers.user_helpers import check_user_validity
from flask import render_template, redirect, url_for, request, flash

@app.route("/")
def products_index():
    (valid, error) = check_user_validity()
    if not valid:
        flash(error)
        return redirect(url_for('login'))
    return render_template("products/index.html")

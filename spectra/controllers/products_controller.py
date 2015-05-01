from spectra import app
from spectra.models import db
from flask import render_template, redirect, url_for, request, session
from IPython import embed

@app.route("/")
def products_index():
    if session.has_key("user"):
        return render_template("products/index.html")
    else:
        return redirect(url_for('login'))
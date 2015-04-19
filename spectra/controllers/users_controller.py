from spectra import app
from flask import render_template
from IPython import embed

from spectra.models.user import User

@app.route("/")
def index():
    users = User.query.all()
    return render_template("users/index.html", users = users)

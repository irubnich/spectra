from spectra import app
from spectra.models import db
from spectra.models.user import User

@app.route("/")
def hello():
    return "Hello World!"

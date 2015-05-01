from flask import Flask
app = Flask(__name__)
app.secret_key = "803997372f9ef872dc0ea97130178764ce3144fe610c12c3"

import spectra.controllers

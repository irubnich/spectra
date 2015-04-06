from flask import Flask
app = Flask(__name__)

import spectra.routes
import spectra.models.user

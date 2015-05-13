from spectra import app
from spectra.models import db
from spectra.models.product import Product
from spectra.controllers.user_helpers import check_user_validity
from flask import render_template, redirect, url_for, request, flash, session

@app.before_request
def init_cart():
    if not session.has_key("cart"):
        session["cart"] = {
            "items": []
        }
    print session["cart"]
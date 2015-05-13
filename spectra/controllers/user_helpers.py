from flask import session, redirect, url_for
from spectra.models.user import User
from spectra.models.salespeople_client import SalespeopleClient
from IPython import embed

def is_logged_in():
    return session.has_key("user")

def set_session(user):
    session["user"] = {
        "id": user.id,
        "type": user.type
    }

def is_allowed():
    return session.has_key("user")
    
def is_client_active(client):
    salesperson_entry = SalespeopleClient.query.filter(SalespeopleClient.client_id == client.id).first()
    if not salesperson_entry:
        return False

    salesperson = User.query.get(salesperson_entry.salesperson_id)
    return client.active and salesperson and salesperson.type == "salesperson" and salesperson.active

def check_user_validity():
    if is_logged_in():
        user = User.query.get(session["user"]["id"])
        if user.type == "client":
            if not is_client_active(user):
                return (False, "You must be associated with a salesperson to access Spectra.")
        return (True, None)
    else:
        return (False, "You must be logged in to access Spectra.")
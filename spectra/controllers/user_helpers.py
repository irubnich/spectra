from flask import session

def is_logged_in():
    return session.has_key("user")

def set_session(user):
    session["user"] = {
        "id": user.id
    }

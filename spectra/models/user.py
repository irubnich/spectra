from spectra.models import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    type = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean)
    date_created = db.Column(db.DateTime)

    def __init__(self, email):
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.email

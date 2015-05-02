from spectra.models import db
import hashlib

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

    def __init__(self, email, type, first_name, last_name, password, active, date_created):
        self.email = email
        self.type = type
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.active = active
        self.date_created = date_created

    @staticmethod
    def authenticate(email, password):
        user = User.query.filter(User.email == email).first()
        if not user:
            return False

        hashed_password = hashlib.sha512(password).hexdigest()
        if user.password == hashed_password:
            return user
            
    def __repr__(self):
        return '<User %r>' % self.email

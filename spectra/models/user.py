from spectra.models import db
from spectra.models.salespeople_client import SalespeopleClient
from spectra.models.complaint import Complaint
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
    discount = db.Column(db.Float)
    commission = db.Column(db.Float)

    def __init__(self, email, type, first_name, last_name, password, active, date_created, discount, commission):
        self.email = email
        self.type = type
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.active = active
        self.date_created = date_created
        self.discount = discount
        self.commission = commission

    def name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def get_salesperson(self):
        if self.type != "client":
            return None

        salesperson_entry = SalespeopleClient.query.filter(SalespeopleClient.client_id == self.id).first()
        if not salesperson_entry:
            return None

        return User.query.get(salesperson_entry.salesperson_id)

    def complaints(self):
        return Complaint.query.filter(Complaint.user_id == self.id)

    def blacklist(self):
        if self.type != "client":
            raise BaseException("Can't blacklist a non-client!")

        self.active = False
        db.session.add(self)
        db.session.commit()

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

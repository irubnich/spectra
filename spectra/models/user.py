from spectra.models import db
from sqlalchemy import desc
from spectra.models.salespeople_client import SalespeopleClient
from spectra.models.rating import Rating
from spectra.models.complaint import Complaint
import hashlib
from datetime import datetime

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

    def rating(self):
        current_rating = Rating.query.filter(Rating.user_id == self.id).order_by(desc(Rating.date)).first()
        if current_rating:
            return current_rating.rating
        else:
            return 5.0

    def rate(self, rater_id, order_id, rating_type):
        # Calculate new rating
        positive_ratings = Rating.query.filter(Rating.user_id == self.id).filter(Rating.rating_type == True).all()
        all_ratings = Rating.query.filter(Rating.user_id == self.id).all()
        if rating_type:
            new_rating = ((float(len(positive_ratings) + 1)) / (len(all_ratings) + 1)) * 5
        else:
            new_rating = (float(len(positive_ratings)) / (len(all_ratings) + 1)) * 5

        new_rating = Rating(self.id, rater_id, order_id, rating_type, new_rating, datetime.now())
        db.session.add(new_rating)
        db.session.commit()
        return new_rating

    # For client
    def get_salesperson(self):
        if self.type != "client":
            return None

        salesperson_entry = SalespeopleClient.query.filter(SalespeopleClient.client_id == self.id).first()
        if not salesperson_entry:
            return None

        return User.query.get(salesperson_entry.salesperson_id)

    # For salesperson
    def get_clients(self):
        if self.type != "salesperson":
            raise BaseException("Can't get clients for a non-salesperson!")

        relations = SalespeopleClient.query.filter(SalespeopleClient.salesperson_id == self.id)
        return map(lambda relation: User.query.get(relation.client_id), relations)

    def complaints(self):
        return Complaint.query.filter(Complaint.user_id == self.id)

    def blacklist(self):
        if self.type != "client":
            raise BaseException("Can't blacklist a non-client!")

        self.deactivate()

    def suspend(self):
        if self.type != "salesperson":
            raise BaseException("Can't suspend a non-salesperson!")

        self.deactivate()

    def deactivate(self):
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

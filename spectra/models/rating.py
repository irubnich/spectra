from spectra.models import db

class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    rater_id = db.Column(db.Integer)
    order_id = db.Column(db.Integer)
    rating_type = db.Column(db.String)
    rating = db.Column(db.Float)
    date = db.Column(db.DateTime)

    def __init__(self, user_id, rater_id, order_id, rating_type, rating, date):
        self.user_id = user_id
        self.rater_id = rater_id
        self.order_id = order_id
        self.rating_type = rating_type
        self.rating = rating
        self.date = date

        def __repr__(self):
            return '<User {0} rated user {1}>'.format(self.rater_id, self.user_id)

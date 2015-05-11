from spectra.models import db

class Complaint(db.Model):
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    complainer_id = db.Column(db.Integer)
    details = db.Column(db.String)
    date = db.Column(db.DateTime)

    def __init__(self, user_id, complainer_id, details, date):
        self.user_id = user_id
        self.complainer_id = complainer_id
        self.details = details
        self.date = date

    def __repr__(self):
        return '<User {0} filed a complaint against user {1}>'.format(self.complainer_id, self.user_id)

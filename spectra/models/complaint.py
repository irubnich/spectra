from spectra.models import db

class Complaint(db.Model):
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    complainer_id = db.Column(db.Integer)
    details = db.Column(db.String)
    date = db.Column(db.DateTime)

    def __init__(self, details):
		self.details = details

    def __repr__(self):
        return '<Complaint %r>' % self.details

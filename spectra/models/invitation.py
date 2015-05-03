from spectra.models import db

class Invitation(db.Model):
    __tablename__ = 'Invitation'

    id = db.Column(db.Integer, primary_key=True)
    salesperson_id = db.Column(db.Integer)
    invite_code = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255))
    user_id = db.Column(db.Integer)
    date = db.Column(db.DateTime)

    def __init__(self, invite_code):
		self.invite_code = invite_code

    def __repr__(self):
        return '<Invitation %r>' % self.invite_code

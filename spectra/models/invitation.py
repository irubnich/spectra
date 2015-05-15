from spectra.models import db

class Invitation(db.Model):
    __tablename__ = 'invitations'

    id = db.Column(db.Integer, primary_key=True)
    salesperson_id = db.Column(db.Integer)
    invite_code = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255))
    user_id = db.Column(db.Integer)
    date = db.Column(db.DateTime)

    def __init__(self, invite_code, salesperson_id, email, date):
        self.invite_code = invite_code
        self.salesperson_id = salesperson_id
        self.email = email
        self.date = date

    def __repr__(self):
        return '<Invitation %r>' % self.invite_code

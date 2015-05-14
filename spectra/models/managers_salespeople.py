from spectra.models import db

class Manager_salespeople(db.Model):
    __tablename__ = 'managers_salespeople'

    id = db.Column(db.Integer, primary_key=True)
    manager_id = db.Column(db.Integer)
    salesperson_id = db.Column(db.Integer)

    def __init__(self, manager_id, salesperson_id):
        self.manager_id = manager_id
        self.salesperson_id = salesperson_id

    def __repr__(self):
        return '<User {0} filed a complaint against user {1}>'.format(self.complainer_id, self.user_id)

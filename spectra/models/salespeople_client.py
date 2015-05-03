from spectra.models import db

class SalespeopleClient(db.Model):
    __tablename__ = 'salespeople_clients'

    id = db.Column(db.Integer, primary_key=True)
    salesperson_id = db.Column(db.Integer)
    client_id = db.Column(db.Integer)

    def __init__(self, salesperson_id, client_id):
        self.salesperson_id = salesperson_id
        self.client_id = client_id

    def __repr__(self):
        return '<Client {0} is associated with Salesperson {1}>'.format(self.client_id, self.salesperson_id)

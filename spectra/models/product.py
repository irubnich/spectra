from spectra.models import db

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    price = db.Column(db.Float)
    category = db.Column(db.String(255))
    inventory = db.Column(db.Integer)
    promotion = db.Column(db.Float)

    def __init__(self, name, description, price, category, inventory, promotion):
		self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.inventory = inventory
        self.promotion = promotion

    def __repr__(self):
        return '<Product %r>' % self.name

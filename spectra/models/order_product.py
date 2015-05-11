from spectra.models import db

class OrderProduct(db.Model):
	__tablename__ = 'order_products'

	id = db.Column(db.Integer, primary_key=True)
	order_id = db.Column(db.Integer)
	product_id = db.Column(db.Integer)    
	quantity = db.Column(db.Integer) 

	def __init__(self, order_id, product_id, quantity):
		self.order_id = order_id
		self.product_id = product_id
		self.quantity = quantity
		
	def __repr__(self):
		return '<OrderProduct %r>' % self.id
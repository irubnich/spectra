from spectra.models import db

class ProductSuggestion(db.Model):
	__tablename__ = 'product_suggestions'

	id = db.Column(db.Integer, primary_key=True)
	salesperson_id = db.Column(db.Integer)
	name = db.Column(db.String(255))
	reason = db.Column(db.String(255))

	def __init__(self, salesperson_id, name, reason):
		self.salesperson_id = salesperson_id
		self.name = name
		self.reason = reason

	def __repr__(self):
		return '<Product Suggestion %r>' % self.id

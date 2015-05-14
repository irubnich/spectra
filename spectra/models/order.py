from spectra.models import db
from spectra.models.rating import Rating

class Order(db.Model):
	__tablename__ = 'orders'

	id = db.Column(db.Integer, primary_key=True)
	client_id = db.Column(db.Integer)
	salesperson_id = db.Column(db.Integer)
	date = db.Column(db.DateTime)
	date_approved = db.Column(db.DateTime)
	date_rejected = db.Column(db.DateTime)
	total = db.Column(db.Integer)
	discount = db.Column(db.Integer)

	def __init__(self, client_id, salesperson_id, date, date_approved, date_rejected, total, discount):
		self.client_id = client_id
		self.salesperson_id = salesperson_id
		self.date = date
		self.date_approved = date_approved
		self.date_rejected = date_rejected
		self.total = total
		self.discount = discount

	def client(self):
		return User.query.get(self.client_id)
		# order = # some query
		# name = order.client().name()

	def salesperson(self):
		return User.query.get(self.salesperson_id)

	def is_rated_by_user(self, user_id):
		rating = Rating.query.filter(Rating.order_id == self.id).filter(Rating.rater_id == user_id).first()
		if rating:
			return True
		return False

	def __repr__(self):
		return '<Order %r>' % self.id

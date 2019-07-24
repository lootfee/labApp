from datetime import datetime
from app import db, login, app
from flask_login import UserMixin
from flask_cors import cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from time import time
import jwt
import requests


followers = db.Table('followers',
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

departments = db.Table('departments',
	db.Column('company_id', db.Integer, db.ForeignKey('company.id')),
	db.Column('dept_id', db.Integer, db.ForeignKey('department.id')),
)

types = db.Table('types',
	db.Column('company_id', db.Integer, db.ForeignKey('company.id')),
	db.Column('type_id', db.Integer, db.ForeignKey('type.id')),
)

suppliers = db.Table('suppliers',
	db.Column('company_id', db.Integer, db.ForeignKey('company.id')),
	db.Column('supplier_id', db.Integer, db.ForeignKey('supplier.id')),
)

'''lot_number = db.Table('lot_number',
	db.Column('product_id', db.Integer, db.ForeignKey('product.id')),
	db.Column('lot_id', db.Integer, db.ForeignKey('lot.id')),
)'''



class Company(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	company_name = db.Column(db.String(128), index=True)
	address = db.Column(db.String(254))
	contact_info = db.Column(db.String(254))
	logo = db.Column(db.String(1000))
	about_me = db.Column(db.String(400))
	products = db.Column(db.Integer, db.ForeignKey('product.id'))
	
	order = db.relationship('Order', backref=db.backref('company', lazy=True))
	
	def __repr__(self):
		return '<Company {}>'.format(self.company_name)
		
	def company_avatar(self, size):
		digest = md5((self.company_name + str(self.id)).encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
		
	#def request_affiliate(self, user):
		#if not self.is_affiliated_to(user):
	#	Affiliates.append(company_id=self.id, user_id=user.id)
			
	def remove_affiliate(self, user):
		return self.affiliate.remove(user)
		
	def is_my_affiliate(self, user):
		return self.affiliate.filter(Affiliates.user_id == user.id, Affiliates.accepted==True).count() > 0
		
	def is_super_admin(self, user):
		return self.affiliate.filter(Affiliates.user_id == user.id, Affiliates.super_admin==True).first()
		
		

class Affiliates(db.Model):
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'), primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
	accepted = db.Column(db.Boolean, default=False)
	qc_access = db.Column(db.Boolean, default=False)
	inv_access = db.Column(db.Boolean, default=False)
	qc_admin = db.Column(db.Boolean, default=False)
	inv_admin = db.Column(db.Boolean, default=False)
	super_admin	= db.Column(db.Boolean, default=False)
	
	company = db.relationship('Company', backref=db.backref('affiliate', lazy='dynamic'))
	users = db.relationship('User', backref=db.backref('affiliate', lazy='dynamic'))
	

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True )
	password_hash = db.Column(db.String(128))
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	about_me = db.Column(db.String(200))
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)
	#affiliate = db.Column(db.Integer, db.ForeignKey('company.id'))
	followed = db.relationship(
		'User', secondary=followers,
		primaryjoin=(followers.c.follower_id == id),
		secondaryjoin=(followers.c.followed_id == id),
		backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
	)
	#companies = db.relationship(
	#	'Company', secondary='affiliates'
	#	backref=db.backref('affiliate', lazy='dynamic')#, lazy='dynamic'
	#)
		
	def __repr__(self):
		return '<User {}>'.format(self.username)
		
	def set_password(self, password):
		self.password_hash = generate_password_hash(password)
		
	def check_password(self, password):
		return check_password_hash(self.password_hash, password)
		
	def avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)
					
	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)
			
	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)
			
	def is_following(self, user):
		return self.followed.filter(followers.c.followed_id == user.id).count() > 0
		
	def followed_posts(self):
		followed = Post.query.join(
			followers, (followers.c.followed_id == Post.user_id)).filter(
				followers.c.follower_id == self.id)
		own = Post.query.filter_by(user_id = self.id)
		return followed.union(own).order_by(Post.timestamp.desc())
		
	def get_reset_password_token(self, expires_in=600):
		return jwt.encode(
			{'reset_password': self.id, 'exp': time() + expires_in},
			app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
			
	@staticmethod
	def verify_reset_password_token(token):
		try:
			id = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
		except:
			return
		return User.query.get(id)
			

@login.user_loader
def load_user(id):
	return User.query.get(int(id))


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(1000))
	url = db.Column(db.String(1000))
	title = db.Column(db.String(1000))
	description = db.Column(db.String(1000))
	image = db.Column(db.String(1000))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
		
	def __repr__(self):
		return '<Post {} {} {} {} {} >'.format(self.body, self.url, self.title, self.description, self.image)


class Department(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), index=True, unique=True)
	company = db.relationship(
		'Company', secondary='departments',
		backref=db.backref('departments', lazy='dynamic'), lazy='dynamic'
	)
	
	def __repr__(self):
		return '<Department {}>'.format(self.name)
		
	def my_depts(company):
		return company.query.filter(departments.c.company_id == company.id).all()
	
	def is_department(self, company):
		return self.company.filter(departments.c.company_id == company.id).all()
		
	def remove_company(self, company):
		if self.is_department(company):
			self.company.remove(company)

	
class Supplier(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), index=True, unique=True)
	address = db.Column(db.String(200), index=True)
	email = db.Column(db.String(120))
	contact = db.Column(db.String(120))
	company = db.relationship(
		'Company', secondary='suppliers',
		backref=db.backref('suppliers', lazy='dynamic'), lazy='dynamic'
	)
	
	def __repr__(self):
		return '<Supplier {} {} {} {}>'.format(self.name, seld.address, self.email, self.contact)
		
	def my_suppliers(company):
		return company.query.filter(suppliers.c.company_id == company.id).all()
		
	def is_supplier(self, company):
		return self.company.filter(suppliers.c.company_id == company.id).count() > 0
		
	def remove_company(self, company):
		if self.is_supplier(company):
			self.company.remove(company)
	
	
class Type(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), index=True, unique=True)
	company = db.relationship(
		'Company', secondary='types',
		backref=db.backref('types', lazy='dynamic'), lazy='dynamic'
	)
	
	def __repr__(self):
		return '<Type {}>'.format(self.name)
		
	def my_types(company):
		return company.query.filter(types.c.company_id == company.id).all()
		
	def is_type(self, company):
		return self.company.filter(types.c.company_id == company.id).count() > 0
		
	def remove_company(self, company):
		if self.is_type(company):
			self.company.remove(company)
	

	
class Product(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	ref_number = db.Column(db.String(100), unique=True)
	name = db.Column(db.String(200), index=True)
	description = db.Column(db.String(100))
	storage_req = db.Column(db.String(50), index=True)
	
	lot_no = db.relationship('Lot', backref=db.backref('ref_no', lazy=True))
		
	def __repr__(self):
		return '<Product {} {} {} {} {} {} {} {}>'.format(self.ref_number, self.product_code, self.name, self.storage_req, self.price, self.min_quantity, self.description, self.min_expiry)


class MyProducts(db.Model):
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'), primary_key=True)
	product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
	min_expiry = db.Column(db.Integer)
	min_quantity = db.Column(db.Integer)
	price = db.Column(db.Numeric(10,2), index=True)
	department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
	type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
	supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
	
	company = db.relationship('Company', backref=db.backref('my_products', lazy='dynamic'))
	product = db.relationship('Product', backref=db.backref('product_of_company', lazy='dynamic'))


class Lot(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	lot_no = db.Column(db.String(50), index=True)
	expiry = db.Column(db.DateTime, index=True)
	product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
	
	item = db.relationship('Item', backref=db.backref('lot_no', lazy=True))
	
	def __repr__(self):
		return '<Lot {}>'.format(self.id)
	
	
class Item(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	lot_id = db.Column(db.Integer, db.ForeignKey('lot.id'))
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
	delivery_id = db.Column(db.Integer, db.ForeignKey('delivery.id'))
	sequence_no = db.Column(db.String(50))
	date_used = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	
	def __repr__(self):
		return '<Item {}{}>'.format(self.id, self.date_used)
	

class Order(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	order_no = db.Column(db.String(50), index=True)
	date_created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	order_creator = db.Column(db.Integer, db.ForeignKey('user.id'))
	review_approved = db.Column(db.DateTime, index=True)
	reviewer = db.Column(db.Integer, db.ForeignKey('user.id'))
	date_submitted = db.Column(db.DateTime, index=True)
	submitted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	
	def __repr__(self):
		return '<Order {}>'.format(self.order_no)

class Purchase(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	purchase_id = db.Column(db.String(50), index=True)
	date_purchased = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	order_id = db.Column(db.Integer, db.ForeignKey('order.id'))

	def __repr__(self):
		return '<Purchase {}>'.format(self.purchase_id, slef.date_purchased)

class Delivery(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	delivery_id = db.Column(db.String(50), index=True)
	date_delivered = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'))
	
	item = db.relationship('Item', backref=db.backref('delivery_date', lazy=True))
	
	def __repr__(self):
		return '<Delivery {}>'.format(self.delivery_id, slef.date_delivered)

'''class OrdersList(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'), primary_key=True)
	quantity = db.Column(db.Integer)
	department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
	date_requested = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<OrdersList {}>'.format(self.prod_id)


class PurchaseOrdersList(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
	price = db.Column(db.Integer, db.ForeignKey('myProducts.price'))
	quantity = db.Column(db.Integer)
	department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
	supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
	date_requested = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class PurchaseOrders(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	order_id = db.Column(db.String(50), index=True)
	date_ordered = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<Orders {}>'.format(self.quantity, slef.date_ordered)'''

	
#class Deliveries(db.Model):
#	id = db.Column(db.Integer, primary_key=True)
#	product_id = db.Column(db.Integer, db.ForeignKey('product.id', use_alter=True))
#	order_id = db.Column(db.Integer, db.ForeignKey('orders.id', use_alter=True))
#	quantity = db.Column(db.Integer)
#	department_id = db.Column(db.Integer, db.ForeignKey('department.id', use_alter=True))
#	date_received = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#	user_id = db.Column(db.Integer, db.ForeignKey('user.id', use_alter=True))
#	item_id = db.Column(db.Integer, db.ForeignKey('item.id', use_alter=True))
#	product = db.relationship('Product', foreign_keys=[product_id], post_update=True, backref=db.backref('product', lazy='dynamic'))
#	orders = db.relationship('Orders', foreign_keys=[order_id], post_update=True, backref=db.backref('orders', lazy='dynamic'))
#	department = db.relationship('Department', foreign_keys=[department_id], post_update=True, backref=db.backref('department', lazy='dynamic'))
#	item = db.relationship('Item', foreign_keys=[item_id], post_update=True, backref=db.backref('item', lazy='dynamic'))
#	user = db.relationship('User', foreign_keys=[user_id], post_update=True, backref=db.backref('user', lazy='dynamic'))
	
#	def __repr__(self):
#		return '<Deliveries {}>'.format(self.quantity, self.date_received)
	
	
	
	
	
	
	

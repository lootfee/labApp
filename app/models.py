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

order_creator = db.Table('order_creator',
	db.Column('order_id', db.Integer, db.ForeignKey('order.id')),
	db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
)

order_submitted_by = db.Table('order_submitted_by',
	db.Column('order_id', db.Integer, db.ForeignKey('order.id')),
	db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
)

purchase_created_by = db.Table('purchase_created_by',
	db.Column('purchase_id', db.Integer, db.ForeignKey('purchase.id')),
	db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
)

purchased_by = db.Table('purchased_by',
	db.Column('purchase_id', db.Integer, db.ForeignKey('purchase.id')),
	db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
)

votes = db.Table('votes',
	db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
	db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
)

upvotes = db.Table('upvotes',
	db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
	db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
)

downvotes = db.Table('downvotes',
	db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
	db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
)


#deliveries = db.Table('deliveries',
#	db.Column('purchase_list_id', db.Integer, db.ForeignKey('purchase_list.id')),
#	db.Column('delivery_id', db.Integer, db.ForeignKey('delivery.id')),
#)



class Company(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	company_name = db.Column(db.String(128), index=True)
	email = db.Column(db.String(120), index=True, unique=True )
	address = db.Column(db.String(254))
	contact_info = db.Column(db.String(254))
	logo = db.Column(db.String(1000))
	about_me = db.Column(db.String(400))
	products = db.Column(db.Integer, db.ForeignKey('product.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
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
		
	def is_qc_supervisor(self, user):
		return self.affiliate.filter(Affiliates.user_id == user.id, Affiliates.qc_supervisor==True).first()
		
	def is_qc_admin(self, user):
		return self.affiliate.filter(Affiliates.user_id == user.id, Affiliates.qc_admin==True).first()
		
	def is_inv_supervisor(self, user):
		return self.affiliate.filter(Affiliates.user_id == user.id, Affiliates.inv_supervisor==True).first()
		
	def is_inv_admin(self, user):
		return self.affiliate.filter(Affiliates.user_id == user.id, Affiliates.inv_admin==True).first()
		
	def is_doc_supervisor(self, user):
		return self.affiliate.filter(Affiliates.user_id == user.id, Affiliates.doc_supervisor==True).first()
		
	def is_doc_admin(self, user):
		return self.affiliate.filter(Affiliates.user_id == user.id, Affiliates.doc_admin==True).first()
		
		

class Affiliates(db.Model):
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'), primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
	accepted = db.Column(db.Boolean, default=False)
	start_date = db.Column(db.DateTime)
	end_date = db.Column(db.DateTime)
	title = db.Column(db.String(64), index=True)
	#qc_access = db.Column(db.Boolean, default=False)
	#inv_access = db.Column(db.Boolean, default=False)
	#doc_access = db.Column(db.Boolean, default=False)
	qc_supervisor = db.Column(db.Boolean, default=False)
	inv_supervisor = db.Column(db.Boolean, default=False)
	doc_supervisor = db.Column(db.Boolean, default=False)
	qc_admin = db.Column(db.Boolean, default=False)
	inv_admin = db.Column(db.Boolean, default=False)
	doc_admin = db.Column(db.Boolean, default=False)
	super_admin	= db.Column(db.Boolean, default=False)
	
	company = db.relationship('Company', backref=db.backref('affiliate', lazy='dynamic'))
	users = db.relationship('User', backref=db.backref('affiliate', lazy='dynamic'))
	

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	firstname = db.Column(db.String(64), index=True)
	lastname = db.Column(db.String(64), index=True)
	username = db.Column(db.String(64), index=True, unique=True)
	email = db.Column(db.String(120), index=True, unique=True )
	password_hash = db.Column(db.String(128))
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	comment = db.relationship('Comment', backref='author', lazy='dynamic')
	comment_reply = db.relationship('CommentReply', backref='author', lazy='dynamic')
	profile_pic = db.Column(db.String(1000))
	about_me = db.Column(db.String(200))
	last_seen = db.Column(db.DateTime, default=datetime.utcnow)
	purchase_added_by = db.relationship('PurchaseList', backref=db.backref('purchase_added_by', lazy=True))
	last_message_read_time = db.Column(db.DateTime)
	followed = db.relationship(
		'User', secondary=followers,
		primaryjoin=(followers.c.follower_id == id),
		secondaryjoin=(followers.c.followed_id == id),
		backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
	)
	
	messages_sent = db.relationship(
		'Message', foreign_keys='Message.sender_id',backref='author', lazy='dynamic'
	)
	
	messages_received = db.relationship(
		'Message',foreign_keys='Message.recipient_id',backref='recipient', lazy='dynamic'
	)
	
	
	order_creator = db.relationship(
		'Order', secondary='order_creator',
		backref=db.backref('order_creator', lazy='dynamic'), lazy='dynamic'
	)
	order_submitted_by = db.relationship(
		'Order', secondary='order_submitted_by',
		backref=db.backref('order_submitted_by', lazy='dynamic'), lazy='dynamic'
	)
	
	purchase_created_by = db.relationship(
		'Purchase', secondary='purchase_created_by',
		backref=db.backref('purchase_created_by', lazy='dynamic'), lazy='dynamic'
	)
	
	purchased_by = db.relationship(
		'Purchase', secondary='purchased_by',
		backref=db.backref('purchased_by', lazy='dynamic'), lazy='dynamic'
	)

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
		
	def new_messages(self):
		last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
		return Message.query.filter_by(recipient=self).filter(Message.timestamp > last_read_time).count()
			

@login.user_loader
def load_user(id):
	return User.query.get(int(id))


class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(10000))
	url = db.Column(db.String(1000))
	title = db.Column(db.String(1000))
	description = db.Column(db.String(1000))
	image = db.Column(db.String(1000))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	comments = db.relationship('Comment', backref=db.backref('post', lazy=True), lazy='dynamic')
	
	voters = db.relationship(
		'User', secondary='votes',
		backref=db.backref('votes', lazy='dynamic'), lazy='dynamic'
	)
	
	upvoters = db.relationship(
		'User', secondary='upvotes',
		backref=db.backref('upvotes', lazy='dynamic'), lazy='dynamic'
	)
	
	downvoters = db.relationship(
		'User', secondary='downvotes',
		backref=db.backref('downvotes', lazy='dynamic'), lazy='dynamic'
	)
	
		
	def voted(self, user):
		return self.voters.filter(votes.c.user_id == user.id).count() > 0
		
	def upvoted(self, user):
		return self.upvoters.filter(upvotes.c.user_id == user.id).count() > 0
		
	def downvoted(self, user):
		return self.downvoters.filter(downvotes.c.user_id == user.id).count() > 0
			
	def upvotes(self, user):
			if not self.voted(user):
				self.upvoters.append(user)
				self.voters.append(user)
			else:
				if self.upvoted(user):
					self.voters.remove(user)
					self.upvoters.remove(user)
				elif self.downvoted(user):
					self.downvoters.remove(user)
					self.upvoters.append(user)
				
				
	def downvotes(self, user):
			if not self.voted(user):
				self.downvoters.append(user)
				self.voters.append(user)
			else:
				if self.downvoted(user):
					self.voters.remove(user)
					self.downvoters.remove(user)
				elif self.upvoted(user):
					self.upvoters.remove(user)
					self.downvoters.append(user)
	
	
	def __repr__(self):
		return '<Post {} {} {} {} {} >'.format(self.body, self.url, self.title, self.description, self.image)


class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(1000))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

	reply = db.relationship('CommentReply', backref=db.backref('comment', lazy=True))
	
	def __repr__(self):
		return '<Comment {}>'.format(self.id)
		
class CommentReply(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.String(1000))
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))

	def __repr__(self):
		return '<Comment {}>'.format(self.id)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(5000))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Message {}>'.format(self.body)
		

class Department(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), index=True, unique=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
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
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
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
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
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
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	lot_no = db.relationship('Lot', backref=db.backref('ref_no', lazy=True))
		
	def __repr__(self):
		return '<Product {} {} {} {} {} {} {} {}>'.format(self.ref_number, self.name, self.storage_req, self.price, self.min_quantity, self.description, self.min_expiry)


class MyProducts(db.Model):
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'), primary_key=True)
	product_id = db.Column(db.Integer, db.ForeignKey('product.id'), primary_key=True)
	min_expiry = db.Column(db.Integer)
	min_quantity = db.Column(db.Integer)
	price = db.Column(db.Numeric(10,2), index=True)
	department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
	type_id = db.Column(db.Integer, db.ForeignKey('type.id'))
	supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	company = db.relationship('Company', backref=db.backref('my_products', lazy='dynamic'))
	product = db.relationship('Product', backref=db.backref('product_of_company', lazy='dynamic'))


class Order(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	order_no = db.Column(db.String(50), index=True, unique=True)
	date_created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	date_submitted = db.Column(db.DateTime, index=True)
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	
	order_list = db.relationship('OrdersList', backref=db.backref('order_list', lazy=True))
	puchase_no = db.relationship('Purchase', backref=db.backref('purchase_no', lazy=True))
	
	def __repr__(self):
		return '<Order {}>'.format(self.order_no)
		
class OrdersList(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	ref_number = db.Column(db.String(100))
	name = db.Column(db.String(200), index=True)
	price = db.Column(db.Numeric(10,2), index=True)
	quantity = db.Column(db.Integer)
	total = db.Column(db.Numeric(10,2))
	order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	
	def __repr__(self):
		return '<OrdersList {}>'.format(self.id)
		
class Purchase(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	purchase_order_no = db.Column(db.String(50), index=True, unique=True)
	#created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
	date_created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	#purchased_by = db.Column(db.Integer, db.ForeignKey('user.id'))
	date_purchased = db.Column(db.DateTime, index=True)
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	order_no = db.Column(db.Integer, db.ForeignKey('order.id'))
	
	purchase_to_purchase_list = db.relationship('PurchaseList', backref=db.backref('purchase_to_purchase_list', lazy=True))
	purchase_to_delivery = db.relationship('Delivery', backref=db.backref('purchase_to_delivery', lazy=True))

	def __repr__(self):
		return '<Purchase {}>'.format(self.purchase_order_no, self.date_purchased)
		
class PurchaseList(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	ref_number = db.Column(db.String(100))
	name = db.Column(db.String(200), index=True)
	price = db.Column(db.Numeric(10,2), index=True)
	quantity = db.Column(db.Integer)
	total = db.Column(db.Numeric(10,2))
	purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	
	purchase_list_to_item = db.relationship('Item', backref=db.backref('purchase_list_to_item', lazy=True))
	
	def __repr__(self):
		return '<PurchaseList {}>'.format(self.id)
		
	#def delivered_qty(self, delivery):
	#	return self.deliveries.filter(deliveries.c.delivery_id == delivery.id).count()


class Delivery(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	delivery_no = db.Column(db.String(50), index=True, unique=True)
	receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	date_delivered = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'))
	
	delivery_to_item = db.relationship('Item', backref=db.backref('delivery_to_item', lazy=True))
	
	def __repr__(self):
		return '<Delivery {}>'.format(self.delivery_no, self.date_delivered)
		
class Item(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	lot_id = db.Column(db.Integer, db.ForeignKey('lot.id'))
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
	purchase_list_id = db.Column(db.Integer, db.ForeignKey('purchase_list.id'))
	delivery_id = db.Column(db.Integer, db.ForeignKey('delivery.id'))
	#sequence_no = db.Column(db.Integer)-use id instead
	date_used = db.Column(db.DateTime, index=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __repr__(self):
		return '<Item {}{}>'.format(self.id)

class Lot(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	lot_no = db.Column(db.String(50), index=True, unique=True)
	expiry = db.Column(db.DateTime, index=True)
	product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	item = db.relationship('Item', backref=db.backref('lot_no', lazy=True))
	
	def __repr__(self):
		return '<Lot {}>'.format(self.id)


class DocumentationDepartment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	department_name = db.Column(db.String(50), index=True, unique=True)
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	document = db.relationship('DocumentName', backref=db.backref('department', lazy=True))
	sections = db.relationship('DocumentSection', backref=db.backref('department', lazy=True))
	versions = db.relationship('DocumentVersion', backref=db.backref('department', lazy=True))
	
	def __repr__(self):
		return '<DocumentationDepartment {}>'.format(self.id)


class DocumentName(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	document_no = db.Column(db.String(50), index=True)
	document_name = db.Column(db.String(50), index=True)
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	department_id = db.Column(db.Integer, db.ForeignKey('documentation_department.id'))
	
	sections = db.relationship('DocumentSection', backref=db.backref('document_name', lazy=True))
	versions = db.relationship('DocumentVersion', backref=db.backref('document_name', lazy=True))
	body = db.relationship('DocumentSectionBody', backref=db.backref('document_name', lazy=True))
	
	def __repr__(self):
		return '<DocumentName {}>'.format(self.id)
		
		
class DocumentSection(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	section_number = db.Column(db.Integer)
	section_title = db.Column(db.String(50))
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	department_id = db.Column(db.Integer, db.ForeignKey('documentation_department.id'))
	document_name_id = db.Column(db.Integer, db.ForeignKey('document_name.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	body = db.relationship('DocumentSectionBody', backref=db.backref('document_section', lazy=True))
	
	def __repr__(self):
		return '<DocumentSection {}>'.format(self.id)

class DocumentSectionBody(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	section_body = db.Column(db.String(50000))
	change_log = db.Column(db.String(400))
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	department_id = db.Column(db.Integer, db.ForeignKey('documentation_department.id'))
	document_name_id = db.Column(db.Integer, db.ForeignKey('document_name.id'))
	document_section_id = db.Column(db.Integer, db.ForeignKey('document_section.id'))
	submitted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
	date_submitted = db.Column(db.DateTime, index=True, default=datetime.utcnow)
		
	def __repr__(self):
		return '<DocumentSectionBody {}>'.format(self.id)
		
class DocumentVersion(db.Model):
	section_id = db.Column(db.Integer, db.ForeignKey('document_section.id'), primary_key=True)
	section_body_id = db.Column(db.Integer, db.ForeignKey('document_section_body.id'), primary_key=True)
	version_no = db.Column(db.Integer)
	reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
	date_reviewed = db.Column(db.DateTime, index=True)
	approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
	date_approved = db.Column(db.DateTime, index=True)
	company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
	department_id = db.Column(db.Integer, db.ForeignKey('documentation_department.id'))
	document_name_id = db.Column(db.Integer, db.ForeignKey('document_name.id'))
	
	section = db.relationship('DocumentSection', backref=db.backref('version', lazy=True))
	body = db.relationship('DocumentSectionBody', backref=db.backref('version', lazy=True))

	def __repr__(self):
		return '<DocumentVersion {}>'.format(self.id)



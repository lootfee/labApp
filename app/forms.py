from flask_wtf import FlaskForm
from app import app, photos
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DecimalField, SelectField, SelectMultipleField, IntegerField, HiddenField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, URL, InputRequired, Regexp
from flask_wtf.file import FileField, FileRequired, FileAllowed
from app.models import User, Product, Item, Department, Supplier, Type, Order

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
	firstname = StringField('First Name', validators=[DataRequired()])
	lastname = StringField('Last Name', validators=[DataRequired()])
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired(), Regexp(regex=r'^(?=\S{8,20}$)(?=.*?\d)(?=.*?[a-z])(?=.*?[A-Z])(?=.*?[^A-Za-z\s0-9])', message="Password must be atleasst 8 characters long, must contain an uppercase letter, a number and a special character.") ])
	password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password', message='Passwords do not match')])
	submit = SubmitField('Register')
	
	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Username already taken!')
			
	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Email is already registered!')

		

class EditProfileForm(FlaskForm):
	firstname = StringField('First Name', validators=[DataRequired()])
	lastname = StringField('Last Name', validators=[DataRequired()])
	username = StringField('Username', validators=[DataRequired()])
	about_me = TextAreaField('About Me', validators=[Length(min=0, max=200)])
	submit = SubmitField('Submit')
	cancel = SubmitField('Cancel')
	
	def __init__(self, original_username, *args, **kwargs):
		super(EditProfileForm, self).__init__(*args, **kwargs)
		self.original_username = original_username
	
	def validate_username(self, username):
		if username.data != self.original_username:
			user = User.query.filter_by(username=self.username.data).first()
			if user is not None:
				raise ValidationError('Username already taken!')
				
class PostForm(FlaskForm):
	post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=1000)])
	url = StringField('Paste URL here', validators=[URL()])
	submit = SubmitField('Submit')
	
class ResetPasswordRequestForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Request Password Reset')
	
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Regexp(regex=r'^(?=\S{8,20}$)(?=.*?\d)(?=.*?[a-z])(?=.*?[A-Z])(?=.*?[^A-Za-z\s0-9])', message="Password must be atleasst 8 characters long, must contain an uppercase letter, a number and a special character.")])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class UserRoleForm(FlaskForm):
	qc_access = BooleanField('QC Access')
	inv_access = BooleanField('Inventory Access')
	qc_admin = BooleanField('QC Admin')
	inv_admin = BooleanField('Inventory Admin')
	super_admin = BooleanField('Super Admin')
	submit = SubmitField('Save')
	cancel = SubmitField('Cancel')


class CompanyRegistrationForm(FlaskForm):
	company_name = StringField('Company Name', validators=[DataRequired()])
	submit = SubmitField('Submit')
	
class CompanyProfileForm(FlaskForm):
	company_name = StringField('Company Name:', validators=[DataRequired()])
	address = TextAreaField('Address:', validators=[Length(min=1, max=1000)])
	contact_info = StringField('Contact info:')
	logo = FileField('Logo:', validators=[FileAllowed(photos)])
	about_me = TextAreaField('About Company:', validators=[Length(min=1, max=3000)], render_kw={"rows": 5, "cols": 150})
	submit = SubmitField('Save')
	cancel = SubmitField('Cancel')
	
class ProductRegistrationForm(FlaskForm):
	reference_number = StringField('Reference Number', validators=[DataRequired()])
	name = StringField('Item Name', validators=[DataRequired()])
	description = StringField('Description', validators=[DataRequired()])
	price = DecimalField('Price', places=2, rounding=None)
	min_quantity = IntegerField('Minimum Quantity')
	min_expiry = IntegerField('Minimum Expiry(Months)')
	storage_req = StringField('Storage Requirement', validators=[DataRequired()])
	department = SelectField('Department', coerce=int, validators=[InputRequired()])
	supplier = SelectField('Supplier', coerce=int, validators=[InputRequired()])
	type = SelectField('Type', coerce=int, validators=[InputRequired()])
	submit = SubmitField('Register')
	
class DepartmentRegistrationForm(FlaskForm):
	dept_name = StringField('Department Name', validators=[DataRequired()])
	submit = SubmitField('Register')
	
	#def validate_dept_name(self, dept_name):
	#	dept = Department.query.filter_by(name=dept_name.data).first()
	#	if dept is not None:
	#		raise ValidationError('Department name already registered!')
			
class DepartmentEditForm(FlaskForm):
	dept_name = StringField('Department Name', validators=[DataRequired()])
	submit = SubmitField('Edit')
	cancel = SubmitField('Cancel')
	
	'''def validate_dept_name(self, dept_name):
		dept = Department.query.filter_by(name=dept_name.data).first()
		if dept is not None:
			raise ValidationError('Department name already registered!')'''
	
class TypeRegistrationForm(FlaskForm):
	type_name = StringField('Type', validators=[DataRequired()])
	submit = SubmitField('Register')
	
	#def validate_type_name(self, type_name):
	#	typ = Type.query.filter_by(name=type_name.data).first()
	#	if typ is not None:
	#		raise ValidationError('Type name already registered!')
			
class TypeEditForm(FlaskForm):
	type_name = StringField('Type', validators=[DataRequired()])
	submit = SubmitField('Register')
	cancel = SubmitField('Cancel')
	
	'''def validate_type_name(self, type_name):
		typ = Type.query.filter_by(name=type_name.data).first()
		if typ is not None:
			raise ValidationError('Type name already registered!')'''
	
class SupplierRegistrationForm(FlaskForm):
	supplier_name = StringField('Supplier Name', validators=[DataRequired()])
	address = StringField('Address', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	contact = StringField('Contact No.', validators=[DataRequired()])
	submit = SubmitField('Register')

	'''def validate_supplier_name(self, supplier_name):
		supplier = Type.query.filter_by(name=supplier_name.data).first()
		if supplier is not None:
			raise ValidationError('Supplier name already registered!')'''
	
#class ItemEntryForm(FlaskForm):
#	department = SelectMultipleField('Select Department', coerce=int)
#	item = SelectMultipleField('Select Product', coerce=int)
	
	#def select_department(request, id):
	#	department = Department.query.get(id)
	#	form = ItemEntryForm(request.POST, obj=item)
	#	form.department.choices = [(d.id, d.name) for d in Department.query.order_by('name')]
	
	#def select_product(request, id):
		#department = ItemEntryForm(request.GET, obj=department)
	#	product = Product.query.get(id)
	#	form = ItemEntryForm(request.POST, obj=item)
	#	form.item.choices = [(p.id, p.name) for p in Product.query.order_by('name')]

class CreateOrderIDForm(FlaskForm):
	order_no = StringField('Create Order ID', validators=[DataRequired()])
	submit = SubmitField('Submit')

	
class InventorySearchForm(FlaskForm):
	search_create_orders = StringField('Search')
	department = SelectField('Department', coerce=int, validators=[InputRequired()])
	#type = SelectField('Type', coerce=int, validators=[InputRequired()])

class OrderListForm(FlaskForm):
	refnum = HiddenField('Reference Number')
	name = HiddenField('Name')
	qty = HiddenField('Quantity')
	price = HiddenField('Price')
	tot_price = HiddenField('Total Price')
	save = SubmitField('Save')
	submit = SubmitField('Submit Order')

	
class DocumentRequestForm(FlaskForm):
	url = StringField('Paste URL here', validators=[URL()])
	submit = SubmitField('Submit')

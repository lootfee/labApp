from flask_wtf import FlaskForm
from app import app, photos
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, DecimalField, SelectField, SelectMultipleField, IntegerField, HiddenField, DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, URL, InputRequired, Regexp
from flask_wtf.file import FileField, FileRequired, FileAllowed
from app.models import User, Product, Item, Department, Supplier, Type, Order, Company, Delivery
from flask_pagedown.fields import PageDownField

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
	firstname = StringField('First Name', validators=[DataRequired()])
	lastname = StringField('Last Name', validators=[DataRequired()])
	username = StringField('Username', validators=[DataRequired(), Length(min=4, max=15)])
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
	username = StringField('Username', validators=[DataRequired(), Length(min=4, max=15)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	profile_pic = FileField('Upload Profile Pic:', validators=[FileAllowed(photos)])
	about_me = TextAreaField('About Me', validators=[Length(min=0, max=200)])
	submit = SubmitField('Submit')
	cancel = SubmitField('Cancel')
	
	def __init__(self, original_username, original_email, *args, **kwargs):
		super(EditProfileForm, self).__init__(*args, **kwargs)
		self.original_username = original_username
		self.original_email = original_email
			
	def validate_username(self, username):
		if username.data != self.original_username:
			user = User.query.filter_by(username=self.username.data).first()
			if user is not None:
				raise ValidationError('Username already taken!')
				
	def validate_email(self, email):
		if email.data != self.original_email:
			user = User.query.filter_by(email=self.email.data).first()
			if user is not None:
				raise ValidationError('Email is already registered!')
				

class PostForm(FlaskForm):
	post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=10000)], render_kw={'maxlength': 10000})
	url = StringField('Paste URL here', validators=[URL()])
	submit_url = SubmitField('Submit with URL')
	submit_text = SubmitField('Submit only text')
	
class CommentForm(FlaskForm):
	comment = TextAreaField('Post a comment', validators=[DataRequired(), Length(min=1, max=1000)], render_kw={'maxlength': 1000})
	submit = SubmitField('Submit')

class MessageFormDirect(FlaskForm):
	message = TextAreaField('Message', validators=[DataRequired(), Length(min=0, max=5000)], render_kw={'maxlength': 5000})
	submit = SubmitField('Submit')
	
class MessageForm(FlaskForm):
	user_search_bar = StringField('To:', validators=[DataRequired()])
	message = TextAreaField('Message', validators=[DataRequired(), Length(min=0, max=5000)], render_kw={'maxlength': 5000})
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
	title = StringField('Title', validators=[DataRequired()])
	doc_supervisor = BooleanField('Document Supervisor')
	inv_supervisor = BooleanField('Inventory Supervisor')
	qc_supervisor = BooleanField('QC Supervisor')
	doc_admin = BooleanField('Document Admin')
	inv_admin = BooleanField('Inventory Admin')
	qc_admin = BooleanField('QC Admin')
	super_admin = BooleanField('Super Admin')
	start_date = DateField('Start date:', validators=[DataRequired()], format='%Y-%m-%d')
	submit = SubmitField('Save')
	cancel = SubmitField('Cancel')


class CompanyRegistrationForm(FlaskForm):
	company_name = StringField('Company Name:', validators=[DataRequired()])
	company_abbrv = StringField('Company Abbreviation:', validators=[DataRequired(), Length(min=1, max=8)], render_kw={"placeholder": "To be used in company documents"})
	email = StringField('Email', validators=[DataRequired(), Email()])
	address = TextAreaField('Address:', validators=[Length(min=1, max=1000)])
	contact_info = StringField('Contact info:', validators=[DataRequired()])
	logo = FileField('Logo:', validators=[FileAllowed(photos)])
	about_me = TextAreaField('About Company:', validators=[Length(min=1, max=3000)], render_kw={"rows": 5, "cols": 150})
	submit = SubmitField('Save')
	cancel = SubmitField('Cancel')
	
	def validate_company_name(self, company_name):
		company = Company.query.filter_by(company_name=company_name.data).first()
		if company is not None:
			raise ValidationError('Company Name already taken! Please be more specific in creating your company name.(e.g. Include branch name or location.)')
	
class CompanyProfileForm(FlaskForm):
	company_name = StringField('Company Name:', validators=[DataRequired()])
	company_abbrv = StringField('Company Abbreviation:', validators=[DataRequired(), Length(min=1, max=8)], render_kw={"placeholder": "To be used in company documents"})
	email = StringField('Email', validators=[DataRequired(), Email()])
	address = TextAreaField('Address:', validators=[Length(min=1, max=1000)])
	contact_info = StringField('Contact info:', validators=[DataRequired()])
	logo = FileField('Logo:', validators=[FileAllowed(photos)])
	about_me = TextAreaField('About Company:', validators=[Length(min=1, max=3000)], render_kw={"rows": 5, "cols": 150})
	submit = SubmitField('Save')
	cancel = SubmitField('Cancel')
	
	def __init__(self, original_company_name, original_email, *args, **kwargs):
		super(CompanyProfileForm, self).__init__(*args, **kwargs)
		self.original_company_name = original_company_name
		self.original_email = original_email
			
	def validate_companyname(self, company_name):
		if company_name.data != self.original_company_name:
			company_name = Company.query.filter_by(company_name=self.company_name.data).first()
			if company_name is not None:
				raise ValidationError('Company Name already taken! Please be more specific in creating your company name.(e.g. Include branch name or location.)')
				
	def validate_email(self, email):
		if email.data != self.original_email:
			company = Company.query.filter_by(email=self.email.data).first()
			if company is not None:
				raise ValidationError('Email is already registered!')
	
class ProductRegistrationForm(FlaskForm):
	reference_number = StringField('Reference Number', validators=[DataRequired()])
	name = StringField('Item Name', validators=[DataRequired()])
	description = StringField('Description', validators=[DataRequired()])
	type = StringField('Type', validators=[DataRequired()])
	price = DecimalField('Price', places=2, rounding=None)
	min_quantity = IntegerField('Minimum Quantity')
	min_expiry = IntegerField('Minimum Expiry(Days)')
	storage_req = StringField('Storage Requirement', validators=[DataRequired()])
	#department = SelectField('Department', coerce=int, validators=[InputRequired()])
	supplier = SelectField('Supplier', coerce=int, validators=[InputRequired()])
	active = BooleanField('Status')
	#type = SelectField('Type', coerce=int, validators=[InputRequired()])
	submit = SubmitField('Register')
	
class EditProductForm(FlaskForm):
	supplier = SelectField('Supplier', coerce=int, validators=[InputRequired()])
	price = DecimalField('Price', places=2, rounding=None)
	min_quantity = IntegerField('Minimum Quantity')
	min_expiry = IntegerField('Minimum Expiry(Days)')
	active = BooleanField('Status')
	submit = SubmitField('Register')
	
class DepartmentRegistrationForm(FlaskForm):
	dept_name = StringField('Department Name', validators=[DataRequired()], render_kw={"placeholder": "ex. Biochemistry"})
	dept_abbrv = StringField('Abbreviation (to be used in order names)', validators=[DataRequired(), Length(min=1, max=5)], render_kw={"placeholder": "ex. BIO"})
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
	

class CreateOrderIDForm(FlaskForm):
	#order_no = StringField('Create Order ID', validators=[DataRequired()])
	department = SelectField('Select Department', coerce=int, validators=[InputRequired()])
	submit = SubmitField('Submit')
	
class CreatePurchaseOrderForm(FlaskForm):
	order_no_purchase_form = StringField('For Order No:', validators=[DataRequired()])
	purchase_order = StringField('Purchase Order No:', validators=[DataRequired()])
	submit = SubmitField('Create')

	
class InventorySearchForm(FlaskForm):
	search_create_orders = StringField('Search')
	department = SelectField('Department', coerce=int, validators=[InputRequired()])
	#type = SelectField('Type', coerce=int, validators=[InputRequired()])

class OrderListForm(FlaskForm):
	supply_id = HiddenField('Supply ID')
	refnum = HiddenField('Reference Number')
	name = HiddenField('Name')
	qty = HiddenField('Quantity')
	price = HiddenField('Price')
	tot_price = HiddenField('Total Price')
	subtotal = HiddenField('Sub Total')
	save = SubmitField('Save')
	submit = SubmitField('Submit')

class EditOrderListForm(FlaskForm):#not used
	orderlist_id = HiddenField('orderlist id')
	edit_qty = StringField('edit_qty')
	total = StringField('total')
	form_save_edit = SubmitField('Save')
	
class AcceptDeliveryForm(FlaskForm):
	delivery_no = StringField('Delivery Order No:', validators=[DataRequired()])
	purchase_no = StringField('Purchase Order No:', validators=[DataRequired()])
	supplier = SelectField('Supplier', coerce=int, validators=[InputRequired()])
	submit = SubmitField('Submit')
	
	'''def validate_delivery_no(self, delivery_no):
		delivery = Delivery.query.filter_by(delivery_no=delivery_no.data).first()
		if delivery is not None:
			raise ValidationError('Delivery Number already registered! Please check that you have entered the correct data or add it to the existing one.')'''
	
class ItemReceiveForm(FlaskForm):
	lot_no = StringField('Lot No:', validators=[DataRequired()])
	expiry = DateField('Expiry:', validators=[DataRequired()], format='%Y-%m-%d')
	quantity = IntegerField('Quantity')
	submit = SubmitField('Submit')
	
class ConsumeItemForm(FlaskForm):
	lot_numbers = SelectField('Lot Number-Item id / Expiry', coerce=int, validators=[InputRequired()])
	submit = SubmitField('Submit')
	
class AccountsQueryForm(FlaskForm):
	start_date = DateField('From:', validators=[DataRequired()], format='%Y-%m-%d')
	end_date = DateField('To:', validators=[DataRequired()], format='%Y-%m-%d')
	supplier = SelectField('Supplier', coerce=int, validators=[InputRequired()])
	department = SelectField('Department', coerce=int, validators=[InputRequired()])
	submit = SubmitField('Generate')
	
#class CreateDepartmentForm(FlaskForm):
#	department_name = StringField('Deparment name:', validators=[DataRequired()])
#	submit = SubmitField('Submit')

class CreateDocumentForm(FlaskForm):
	dept_name = StringField('Deparment name:', validators=[DataRequired()], render_kw={'readonly': True})
	document_no = StringField('Document id:', validators=[DataRequired()], render_kw={"placeholder": "ex. SOP-001"})
	document_name = StringField('Document name:', validators=[DataRequired()], render_kw={"placeholder": "ex. GLUCOSE"})
	submit = SubmitField('Submit')
	
class CreateDocumentSectionForm(FlaskForm):
	section_number = IntegerField('Section Number', validators=[DataRequired()])
	section_title = StringField('Section title:', validators=[DataRequired()])
	submit = SubmitField('Submit')
	
class EditDocumentSectionForm(FlaskForm):
	section_id = HiddenField('Section id:', validators=[DataRequired()])
	edit_section_number = IntegerField('Section Number', validators=[DataRequired()])
	edit_section_title = StringField('Section title:', validators=[DataRequired()])
	edit_submit = SubmitField('Submit')
	
class EditDocumentBodyForm(FlaskForm):
	body = PageDownField('Edit Document', validators=[DataRequired()])
	changelog = StringField('Changelog:')
	submit = SubmitField('Submit')
	
class DocumentSubmitForm(FlaskForm):
	submit_section_id = HiddenField('Section id:', validators=[DataRequired()])
	submit_section_body_id = HiddenField('Section body id:', validators=[DataRequired()])
	submit_company_id = HiddenField('Company id:', validators=[DataRequired()])
	submit_department_id = HiddenField('Department id:', validators=[DataRequired()])
	submit_document_name_id = HiddenField('Document id:', validators=[DataRequired()])
	submit = SubmitField('Submit for review')
	
class RegisterMachineForm(FlaskForm):
	machine_name = StringField('Machine name', validators=[DataRequired()])
	#department = SelectField('Department', coerce=int, validators=[InputRequired()])
	submit = SubmitField('Submit')
	
class RegisterAnalyteForm(FlaskForm):
	analyte = StringField('Analyte', validators=[DataRequired()], render_kw={"placeholder": "ex. GLUC3, ALB2, etc."})
	unit = StringField('Unit', validators=[DataRequired()])
	#machine = SelectField('Machine', coerce=int, validators=[InputRequired()])
	#department = SelectField('Department', coerce=int, validators=[InputRequired()])
	submit = SubmitField('Submit')
	
class RegisterReagentLotForm(FlaskForm):
	analyte = SelectField('Analyte', coerce=int, validators=[InputRequired()])
	reagent_lot_no = StringField('Lot No', validators=[DataRequired()])
	reagent_expiry = DateField('Expiry:', validators=[DataRequired()], format='%Y-%m-%d', render_kw={"type": "date"})
	submit = SubmitField('Submit')
	
class RegisterControlForm(FlaskForm):
	control_name = StringField('Control name', validators=[DataRequired()])
	submit = SubmitField('Submit')
	
class RegisterQCLotForm(FlaskForm):
	control = SelectField('Control', coerce=int, validators=[InputRequired()])
	control_lot_no = StringField('Lot No', validators=[DataRequired()])
	control_expiry = DateField('Expiry:', validators=[DataRequired()], format='%Y-%m-%d', render_kw={"type": "date"})
	submit = SubmitField('Submit')
	
class QCResultForm(FlaskForm):
	start_date = DateField('From:', validators=[DataRequired()], format='%Y-%m-%d', render_kw={"type": "date"})
	end_date = DateField('To:', validators=[DataRequired()], format='%Y-%m-%d', render_kw={"type": "date"})
	analyte = SelectField('Analyte', coerce=int, validators=[InputRequired()])
	unit = SelectField('Unit', coerce=int, validators=[InputRequired()])
	reagent_lot = SelectField('Reagent Lot', coerce=int, validators=[InputRequired()])
	machine = SelectField('Machine', coerce=int, validators=[InputRequired()])
	control1 = SelectField('Control 1', coerce=int, validators=[InputRequired()])
	control1_mean = DecimalField('Control 1 Mean', validators=[DataRequired()])
	control1_sd = DecimalField('Control 1 SD', validators=[DataRequired()])
	control2 = SelectField('Control 2', coerce=int, validators=[InputRequired()])
	control2_mean = DecimalField('Control 2 Mean', validators=[DataRequired()])
	control2_sd = DecimalField('Control 2 SD', validators=[DataRequired()])
	control3 = SelectField('Control 3', coerce=int, validators=[InputRequired()])
	control3_mean = DecimalField('Control 3 Mean', validators=[DataRequired()])
	control3_sd = DecimalField('Control 3 SD', validators=[DataRequired()])
	run_date = DateField('Date:', validators=[DataRequired()], format='%Y-%m-%d')
	qc_data_lvl1 = DecimalField('Level 1')
	qc_data_lvl2 = DecimalField('Level 2')
	qc_data_lvl3 = DecimalField('Level 3')
	search = SubmitField('Search')
	submit = SubmitField('Submit')
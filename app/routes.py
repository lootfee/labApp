from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from flask_cors import CORS, cross_origin
from werkzeug.urls import url_parse
from app import app, db, photos
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm, DocumentRequestForm, ProductRegistrationForm, DepartmentRegistrationForm, DepartmentEditForm, TypeRegistrationForm, TypeEditForm, SupplierRegistrationForm, InventorySearchForm, CompanyRegistrationForm, CompanyProfileForm, UserRoleForm, CreateOrderIDForm, OrderListForm, EditOrderListForm, CreatePurchaseOrderForm, ItemReceiveForm, AcceptDeliveryForm, ConsumeItemForm
from app.models import User, Post, Product, Item, Department, Supplier, Type, Order, Company, Affiliates, MyProducts, OrdersList, Purchase, PurchaseList, Delivery, Item, Lot
from datetime import datetime, timedelta
from app.email import send_password_reset_email
from link_preview import link_preview
import requests



@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()
		


@app.route('/index', methods=['GET', 'POST'])
@login_required
@cross_origin()
def index():
	user = User.query.filter_by(username=current_user.username).first_or_404()
	form = PostForm()
	if form.validate_on_submit():
		link_preview = 'https://api.linkpreview.net?key=5c6acce458459f41f44caa960c51d28fa218af3f05e30&q={}'.format(form.url.data)
		response = requests.request("POST", link_preview)
		results = response.json()
		title = results['title']
		description = results['description']
		image = results['image']
		post = Post(body=form.post.data, url=form.url.data, title=title, description=description, image=image, author=current_user)
		db.session.add(post)
		db.session.commit()
		return redirect(url_for('index'))
	page = request.args.get('page', 1, type=int)
	posts = current_user.followed_posts().paginate(
		page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('index', page=posts.next_num) \
		if posts.has_next else None
	prev_url = url_for('index', page=posts.prev_num) \
		if posts.has_prev else None
	return render_template('index.html', title='Home', form=form, posts=posts.items, next_url=next_url, prev_url=prev_url, user=user)

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))	
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form =RegistrationForm()
	if form.validate_on_submit():
		user = User(firstname=form.firstname.data, lastname=form.lastname.data, username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash("Thank you for registering!")
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)
	
@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('login'))	

@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	page = request.args.get('page', 1, type=int)
	form = CompanyRegistrationForm()
	if form.validate_on_submit():
		company = Company(company_name=form.company_name.data)
		db.session.add(company)
		db.session.commit()
		accept = Affiliates(accepted=True)
		accept.user_id = current_user.id
		company.affiliate.append(accept)
		db.session.commit()
		return redirect(url_for('user', username=user.username))
	my_affiliates = Affiliates.query.filter_by(user_id=user.id, accepted=True).all()
	#for affiliate in my_affiliates:
	#	affiliate.comp_id = affiliate.company_id
		#affiliate.company = Company.query.filter_by(id=affiliate.company_id).first()
	posts = user.posts.order_by(Post.timestamp.desc()).paginate(
		page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
	prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
	return render_template('user.html', title=user.username, user=user, posts=posts.items, prev_url=prev_url, next_url=next_url, form=form, my_affiliates=my_affiliates)
		

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	user = User.query.filter_by(username=current_user.username).first_or_404()
	form = EditProfileForm(current_user.username)
	if form.submit.data:
		if form.validate_on_submit():
			current_user.firstname = form.firstname.data
			current_user.lastname = form.lastname.data
			current_user.username = form.username.data
			current_user.about_me = form.about_me.data
			if form.profile_pic.data:
				profile_pic_filename = photos.save(form.profile_pic.data)
				current_user.profile_pic = photos.url(profile_pic_filename)
			db.session.commit()
			flash('Your changes has been saved!')
			return redirect(url_for('user', username=current_user.username))
	elif request.method == 'GET':
		form.firstname.data = current_user.firstname
		form.lastname.data = current_user.lastname
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', title='Edit Profile', form=form, user=user)
	
@app.route('/follow/<username>')
@login_required
def follow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('User {} not found.'.format(username))
		return redirect(url_for('index'))
	if user == current_user:
		flash('You cannot follow yourself!')
		return redirect(url_for('user', username=username))
	current_user.follow(user)
	db.session.commit()
	flash('You just followed {}!'.format(username))
	return redirect(url_for('user', username=username))
	
@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
	user = User.query.filter_by(username=username).first()
	if user is None:
		flash('User {} not found.'.format(username))
		return redirect(url_for('index'))
	if user == current_user:
		flash('You cannot unfollow yourself!')
		return redirect(url_for('user', username=username))
	current_user.unfollow(user)
	db.session.commit()
	flash('You just unfollowed {}!'.format(username))
	return redirect(url_for('user', username=username))
	
@app.route('/explore')
@cross_origin()
def explore():
	user = User.query.filter_by(username=current_user.username).first()
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.timestamp.desc()).paginate(
		page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('explore', page=posts.next_num) \
		if posts.has_next else None
	prev_url = url_for('explore', page=posts.prev_num) \
		if posts.has_prev else None
	return render_template('index.html', title='Global', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def post(id):
	user = User.query.filter_by(username=current_user.username).first()
	post = Post.query.filter_by(id=id).first_or_404()
	upvotes = post.upvoters.count()
	downvotes = post.downvoters.count()
	return render_template('post.html', title='Post', post=post, upvotes=upvotes, downvotes=downvotes)
	
@app.route('/upvote/<int:id>', methods=['GET', 'POST'])
@login_required
def upvote(id):
	user = User.query.filter_by(username=current_user.username).first()
	post = Post.query.filter_by(id=id).first_or_404()
	post.upvotes(user)
	db.session.commit()
	return redirect(url_for('post', id=post.id))
	
@app.route('/downvote/<int:id>', methods=['GET', 'POST'])
@login_required
def downvote(id):
	user = User.query.filter_by(username=current_user.username).first()
	post = Post.query.filter_by(id=id).first_or_404()
	post.downvotes(user)
	db.session.commit()
	return redirect(url_for('post', id=post.id))
	
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = ResetPasswordRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			send_password_reset_email(user)
		flash('Check your email for instructions on how to reset your password.')
		return redirect(url_for('login'))
	return render_template('reset_password_request.html', title='Reset Password', form=form)
	
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)
	
@app.route('/company/<company_name>', methods=['GET', 'POST'])
@login_required
def company(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	affiliates = Affiliates.query.filter_by(company_id=company.id, accepted=True).all()
	pending_affiliates = Affiliates.query.filter_by(company_id=company.id, accepted=False).all()
	is_my_affiliate = company.is_my_affiliate(user)
	is_super_admin = company.is_super_admin(user)
	form = CompanyProfileForm()
	if form.submit.data:
		if form.validate_on_submit():
			company.company_name = form.company_name.data
			company.about_me = form.about_me.data
			company.address = form.address.data
			company.contact_info = form.contact_info.data
			if form.logo.data:
				logo_filename = photos.save(form.logo.data)
				company.logo = photos.url(logo_filename)
			db.session.commit()
			flash('Your changes has been saved!')
			return redirect(url_for('company', company_name=company.company_name))
		else:
			flash('Unable to update changes, please complete missing fields!')
	elif request.method == 'GET':
		form.company_name.data = company.company_name
		if company.about_me:
			form.about_me.data = company.about_me
		if company.address:
			form.address.data = company.address
		if company.logo:
			form.logo.data = company.logo
		if company.contact_info:
			form.contact_info.data = company.contact_info
	return render_template('company.html', form=form, company=company, user=user, affiliates=affiliates, pending_affiliates=pending_affiliates, is_my_affiliate=is_my_affiliate, is_super_admin=is_super_admin)

@app.route('/accept_affiliate/<int:user_id>, <int:comp_id>')
@login_required
def accept_affiliate(user_id, comp_id):
	company = Company.query.filter_by(id=comp_id).first_or_404()
	pending_affiliate = Affiliates.query.filter_by(user_id=user_id, company_id=comp_id, accepted=False).first()
	#user = User.query.filter_by(username=current_user.username).first_or_404()
	#if user.id == pending_affiliate.user_id:
	pending_affiliate.accepted = True
	db.session.commit()
	return redirect(url_for('admin', company_name=company.company_name))
	
@app.route('/delete_affiliate/<int:user_id>, <int:comp_id>')
@login_required
def delete_affiliate(user_id, comp_id):
	company = Company.query.filter_by(id=comp_id).first_or_404()
	#user = User.query.filter(id==user_id).first_or_404()
	affiliate = Affiliates.query.filter_by(user_id=user_id, company_id=comp_id).first()
	#affiliate.accepted = None
	#company.remove_affiliate(affiliate)
	db.session.delete(affiliate)
	db.session.commit()
	return redirect(url_for('admin', company_name=company.company_name))

@app.route('/manage_affiliate/<int:user_id>, <int:comp_id>', methods=['GET', 'POST'])
@login_required
def manage_affiliate(user_id, comp_id):
	company = Company.query.filter_by(id=comp_id).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	affiliate = Affiliates.query.filter_by(user_id=user_id, company_id=comp_id, accepted=True).first()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	form = UserRoleForm()
	if form.submit.data:
		if form.validate_on_submit():
			affiliate.title = form.title.data
			affiliate.qc_access = form.qc_access.data
			affiliate.inv_access = form.inv_access.data
			affiliate.qc_admin = form.qc_admin.data
			affiliate.inv_admin = form.inv_admin.data
			affiliate.super_admin = form.super_admin.data
			if form.qc_admin.data:
				affiliate.qc_access = True
			if form.inv_admin.data:
				affiliate.inv_access = True
			if form.super_admin.data:
				affiliate.qc_access = True
				affiliate.inv_access = True
				affiliate.qc_admin = True
				affiliate.inv_admin = True
			db.session.commit()
			flash('Your changes has been saved!')
			return redirect(url_for('admin', company_name=company.company_name))
	elif request.method == 'GET':
		form.title.data = affiliate.title
		form.qc_access.data = affiliate.qc_access
		form.inv_access.data = affiliate.inv_access
		form.qc_admin.data = affiliate.qc_admin
		form.inv_admin.data = affiliate.inv_admin
		form.super_admin.data = affiliate.super_admin
	return render_template('manage_affiliate_role.html', user=user, form=form, company=company, affiliate=affiliate, is_my_affiliate=is_my_affiliate, is_super_admin=is_super_admin)

@app.route('/request_affiliate/<company_name>', methods=['GET', 'POST'])
@login_required
def request_affiliate(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	#request_query_false = Affiliates.query.filter_by(user_id=current_user.id, company_id=company.id, accepted=False).first_or_404()
	#request_query_true = Affiliates.query.filter_by(user_id=current_user.id, company_id=company.id, accepted=True).first_or_404()
	request = Affiliates(user_id=current_user.id, company_id=company.id)
	company.affiliate.append(request)
	db.session.commit()
	flash('Affiliate request sent!')
	return redirect(url_for('company', company_name=company.company_name))
	
	
@app.route('/admin/<company_name>', methods=['GET', 'POST'])
@login_required
def admin(company_name):
	form = UserRoleForm()
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	affiliates = Affiliates.query.filter_by(company_id=company.id, accepted=True).all()
	for affiliate in affiliates:
		affiliate.this_affiliate = affiliate.users.username
		this_aff = affiliate.this_affiliate
	pending_affiliates = Affiliates.query.filter_by(company_id=company.id, accepted=False).all()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if is_my_affiliate:
		return render_template('admin.html', title='Admin', user=user, form=form, company=company, affiliates=affiliates, pending_affiliates=pending_affiliates, is_my_affiliate=is_my_affiliate, this_aff=this_aff, is_super_admin=is_super_admin)
	else:
		return redirect(url_for('company', company_name=company.company_name))
				
				
@app.route('/calculators')
def calculators():
	return render_template('calculators.html', title='Calculators', user=user)
	

@app.route('/<company_name>/quality_control', methods=['GET', 'POST'])
@login_required
def quality_control(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	affiliate = Affiliates.query.filter_by(user_id=user.id, company_id=company.id, accepted=True).first()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	return render_template('quality_control.html', title='Quality Control', user=user, company=company, is_super_admin=is_super_admin)

@app.route('/quality_control_sample')
def quality_control_sample():
	return render_template('quality_control_sample.html', title='Quality Control')
	
@app.route('/inventory_management_sample')	
def inventory_management_sample():
	return render_template('inventory_management/inventory_overview_sample.html', title='Inventory Overview')
	
@app.route('/<company_name>/inventory_management/overview', methods=['GET', 'POST'])	
@login_required
def inventory_management(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	my_products = MyProducts.query.all()
	for my_p in my_products:
		my_p.name = Product.query.filter_by(id=my_p.product_id).first().name
		my_p.ref_number = Product.query.filter_by(id=my_p.product_id).first().ref_number
		my_p.description = Product.query.filter_by(id=my_p.product_id).first().description
		my_p.storage_req = Product.query.filter_by(id=my_p.product_id).first().storage_req
		my_p.min_quantity = MyProducts.query.filter_by(product_id=my_p.product_id).first().min_quantity
		my_p.min_expiry = MyProducts.query.filter_by(product_id=my_p.product_id).first().min_expiry
		my_p.dept_name = Department.query.filter_by(id=my_p.department_id).first().name
		my_p.type_name = Type.query.filter_by(id=my_p.type_id).first().name
		my_p.supplier_name = Supplier.query.filter_by(id=my_p.supplier_id).first().name
	item_query = Item.query.filter_by(date_used=None).all()
	for i in item_query:
		i.lot_num = Lot.query.filter_by(id=i.lot_id).first().lot_no
		i.expiry = Lot.query.filter_by(id=i.lot_id).first().expiry
		i.quantity = Item.query.filter_by(lot_id=i.lot_id, product_id=my_p.product_id, date_used=None).count()
		i.less_quantity = my_p.min_quantity <= i.quantity
		i.min_expiry = datetime.utcnow() + timedelta(days=my_p.min_expiry)
		i.greater_expiry =  (i.expiry < i.min_expiry)
	return render_template('inventory_management/inventory_overview.html', title='Inventory Overview', company=company, is_super_admin=is_super_admin)
	#return redirect(url_for('inventory', company_name=company.company_name))
	


@app.route('/<company_name>/inventory_management/products', methods=['GET', 'POST'])
@login_required
def products(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	dept = company.departments
	dept_list = [(d.id, d.name) for d in dept]
	type = company.types
	type_list = [(t.id, t.name) for t in type]
	supplier = company.suppliers
	supplier_list = [(s.id, s.name) for s in supplier]
	form = ProductRegistrationForm()
	form.department.choices = dept_list
	form.type.choices = type_list
	form.supplier.choices = supplier_list
	if form.validate_on_submit():
		raw_refnum = form.reference_number.data
		alnum_refnum = ''.join(e for e in raw_refnum if e.isalnum())
		prod = Product.query.filter_by(ref_number=alnum_refnum).first()
		if prod:
			p = MyProducts(company_id=company.id, product_id=product.id, price=form.price.data, min_expiry=form.min_expiry.data, min_quantity=form.min_quantity.data, department_id=form.department.data, type_id=form.type.data, supplier_id=form.supplier.data)
			db.session.add(p)
			db.session.commit()
		else:
			product = Product(ref_number=alnum_refnum, name=form.name.data, description=form.description.data, storage_req=form.storage_req.data)
			db.session.add(product)
			db.session.commit()
			p = MyProducts(company_id=company.id, product_id=product.id, price=form.price.data, min_expiry=form.min_expiry.data, min_quantity=form.min_quantity.data, department_id=form.department.data, type_id=form.type.data, supplier_id=form.supplier.data)
			db.session.add(p)
			db.session.commit()
		return redirect(url_for('products', company_name=company.company_name))
	products = Product.query.order_by(Product.name.asc()).all()
	my_products = MyProducts.query.all()
	for my_p in my_products:
		my_p.name = Product.query.filter_by(id=my_p.product_id).first().name
		my_p.ref_number = Product.query.filter_by(id=my_p.product_id).first().ref_number
		my_p.description = Product.query.filter_by(id=my_p.product_id).first().description
		my_p.storage_req = Product.query.filter_by(id=my_p.product_id).first().storage_req
		my_p.min_quantity = MyProducts.query.filter_by(product_id=my_p.product_id).first().min_quantity
		my_p.min_expiry = MyProducts.query.filter_by(product_id=my_p.product_id).first().min_expiry
		my_p.dept_name = Department.query.filter_by(id=my_p.department_id).first().name
		my_p.type_name = Type.query.filter_by(id=my_p.type_id).first().name
		my_p.supplier_name = Supplier.query.filter_by(id=my_p.supplier_id).first().name
	return render_template('inventory_management/products.html', title='Manage Products', user=user, form=form, products=products, company=company, is_super_admin=is_super_admin, my_products=my_products)
	

@app.route('/delete_product/<int:prod_id>, <int:comp_id>')	
@login_required	
def delete_product(prod_id, comp_id):
    product = MyProduct.query.filter_by(product_id=prod_id, company_id=comp_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product has been deleted.')
    return redirect(url_for('products', company_name=company.company_name))	


@app.route('/<company_name>/inventory_management/inventory', methods=['GET', 'POST'])
@login_required
def inventory(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	orders = Order.query.filter_by(company_id=company.id).first()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	dept = company.departments.order_by(Department.name.asc())
	products = Product.query.order_by(Product.name.asc())
	my_products = MyProducts.query.all()
	for my_p in my_products:
		my_p.name = Product.query.filter_by(id=my_p.product_id).first().name
		my_p.ref_number = Product.query.filter_by(id=my_p.product_id).first().ref_number
		my_p.description = Product.query.filter_by(id=my_p.product_id).first().description
		my_p.dept = Department.query.filter_by(id=my_p.department_id).first().name
		#my_p.stocks = Item.query.filter_by(product_id=my_p.product_id, date_used=None).count()
		my_p.min_quantity = MyProducts.query.filter_by(product_id=my_p.product_id).first().min_quantity
		my_p.min_expiry = MyProducts.query.filter_by(product_id=my_p.product_id).first().min_expiry
		my_p.item_query = Item.query.filter_by(product_id=my_p.product_id, date_used=None).all()
		#my_p.lot_list = []
		for i in my_p.item_query:
			i.lot_num = Lot.query.filter_by(id=i.lot_id).first().lot_no
			i.expiry = Lot.query.filter_by(id=i.lot_id).first().expiry
			i.quantity = Item.query.filter_by(lot_id=i.lot_id, product_id=my_p.product_id, date_used=None).count()
			i.min_expiry = datetime.utcnow() + timedelta(days=my_p.min_expiry)
			i.greater_expiry =  (i.expiry < i.min_expiry)
		'''	my_p.lot_list.append(i.lot_num)
		my_p.count_lot_no_list = dict((x,my_p.lot_list.count(x)) for x in set(my_p.lot_list))
		for j in my_p.item_query:
			for l in my_p.count_lot_no_list:
				j.lot_query = Lot.query.filter_by(lot_no=l).first().lot_no
				j.lot_qty = my_p.count_lot_no_list[l]
				j.lot_expiry = Lot.query.filter_by(lot_no=l).first().expiry
				j.min_expiry = datetime.utcnow() - timedelta(days=my_p.min_expiry)
				j.greater_expiry =  (j.lot_expiry < j.min_expiry)'''
		'''for l in my_p.count_lot_no_list:
			lot_query = Lot.query.filter_by(lot_no=l).first()
			lot_qty = my_p.count_lot_no_list[l]
			my_p.lot_expiry = Lot.query.filter_by(lot_no=l).first().expiry
			min_expiry = datetime.utcnow() - timedelta(days=my_p.min_expiry)
			greater_expiry =  (my_p.lot_expiry < min_expiry)'''
		'''for l in my_p.count_lot_no_list:
			l : {
				lot_expiry : Lot.query.filter_by(lot_no=l).first().expiry.strftime('%d-%m-%Y'),
				'min_expiry' : datetime.utcnow() - timedelta(days=my_p.min_expiry),
				'greater_expiry' : ('lot_expiry' < 'min_expiry')
			}
			print(l[lot_expiry])
			lot_query = Lot.query.filter_by(lot_no=l).first()
			lot_qty = my_p.count_lot_no_list[l]
			my_p.lot_expiry = Lot.query.filter_by(lot_no=l).first().expiry
			lot_expiry = Lot.query.filter_by(lot_no=l).first().expiry
			min_expiry = datetime.utcnow() - timedelta(days=my_p.min_expiry)
			greater_expiry =  (my_p.lot_expiry < min_expiry)'''
		
	return render_template('inventory_management/inventory.html', title='Inventory', user=user, company=company, is_super_admin=is_super_admin, is_my_affiliate=is_my_affiliate, my_products=my_products, orders=orders, dept=dept)

@app.route('/<company_name>/consume_item/<ref_number>', methods=['GET', 'POST'])
@login_required	
def consume_item(company_name, ref_number):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	product = Product.query.filter_by(ref_number=ref_number).first()
	min_expiry = MyProducts.query.filter_by(product_id=product.id).first().min_expiry
	#product_id = Product.query.filter_by(ref_number=ref_number).first().id
	item_query = Item.query.filter_by(product_id=product.id, date_used=None).all()
	for i in item_query:
		i.lot_num = Lot.query.filter_by(id=i.lot_id).first().lot_no
		i.expiry = Lot.query.filter_by(id=i.lot_id).first().expiry
		i.quantity = Item.query.filter_by(lot_id=i.lot_id, product_id=product.id, date_used=None).count()
		i.min_expiry = datetime.utcnow() + timedelta(days=min_expiry)
		i.greater_expiry =  (i.expiry < i.min_expiry)
	form = ConsumeItemForm()
	#lot_list = [(l.lot_id, l.lot_num) for l in item_query]
	#form.lot_numbers.choices = lot_list
	if form.validate_on_submit():
		#lot_num_id = Lot.query.filter_by(id=form.lot_numbers.data).first()
		use_item = Item.query.filter_by(product_id=product.id, lot_id=form.lot_numbers.data, date_used=None).first()
		use_item.date_used = datetime.utcnow()
		db.session.commit()
		return redirect(url_for('inventory', company_name=company.company_name))
	return render_template('inventory_management/consume.html', title='Consume supply', user=user, company=company, is_super_admin=is_super_admin, is_my_affiliate=is_my_affiliate, product=product, item_query=item_query, form=form)

@app.route('/<company_name>/inventory_management/orders', methods=['GET', 'POST'])
@login_required
def orders(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	orders = Order.query.filter_by(company_id=company.id).order_by(Order.date_created.desc()).all()
	for order in orders:
		order.purchase_order = Purchase.query.filter_by(order_no=order.id).first()
	purchases = Purchase.query.filter_by(company_id=company.id).all()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	form = CreateOrderIDForm()
	form1 = CreatePurchaseOrderForm()
	if form.validate_on_submit():
		order = Order(order_no=form.order_no.data, company_id=company.id)
		db.session.add(order)
		order.order_creator.append(user)
		db.session.commit()
		return redirect (url_for('create_orders', company_name=company.company_name, order_no=order.order_no))
	if form1.validate_on_submit():
		order_id = Order.query.filter_by(order_no=form1.order_no_purchase_form.data).first().id
		purchase = Purchase(purchase_order_no=form1.purchase_order.data, company_id=company.id, order_no=order_id)
		db.session.add(purchase)
		purchase.purchase_created_by.append(user)
		db.session.commit()
		purchase_list = OrdersList.query.filter_by(order_id=order_id).all()
		for i in purchase_list:
			list = PurchaseList(ref_number=i.ref_number, name=i.name, price=i.price, quantity=i.quantity, total=i.total, purchase_id=purchase.id, user_id=i.user_id)
			db.session.add(list)
			db.session.commit()
		return redirect (url_for('purchases', company_name=company.company_name))
	return render_template('inventory_management/orders.html', title='Orders', user=user, company=company, form=form, form1=form1, orders=orders, is_my_affiliate=is_my_affiliate, is_super_admin=is_super_admin, purchases=purchases)



@app.route('/<company_name>/inventory_management/create_orders/<order_no>', methods=['GET', 'POST'])
@login_required
def create_orders(company_name, order_no):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	order = Order.query.filter_by(order_no=order_no).first_or_404()
	order_list = OrdersList.query.filter_by(order_id=order.id).all()
	for list in order_list:
		list.user = User.query.filter_by(id=list.user_id).first()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	dept = company.departments.order_by(Department.name.asc())
	#dept_list = [(0, 'All')] + [(d.id, d.name) for d in dept]
	#type = Type.query.all()
	#type_list = [(0, 'All')] + [(t.id, t.name) for t in type]
	#form1 = InventorySearchForm()
	#form1.department.choices = dept_list
	#form1.type.choices = type_list
	#dept_id = form1.department.data
	#type_id= form1.type.data
	products = Product.query.order_by(Product.name.asc())
	my_products = MyProducts.query.all()
	for my_p in my_products:
		my_p.name = Product.query.filter_by(id=my_p.product_id).first().name
		my_p.ref_number = Product.query.filter_by(id=my_p.product_id).first().ref_number
		my_p.description = Product.query.filter_by(id=my_p.product_id).first().description
		my_p.department = Department.query.filter_by(id=my_p.department_id).first().name
	form = OrderListForm()
	if form.save.data:
		refnum_list = request.form.getlist('refnum')
		name_list = request.form.getlist('name')
		price_list = request.form.getlist('price')
		qty_list = request.form.getlist('qty')
		tot_list = request.form.getlist('tot_price')
		#for i in refnum_list, price_list in range(0, len(refnum_list) ):
		for i in range(0, len(refnum_list) ):
			#print(refnum_list[i], name_list[i])
		#for refnum_list, name_list, price_list, qty_list, tot_list in range(0, len(refnum_list)):
			list = OrdersList(ref_number=refnum_list[i], name=name_list[i], price=price_list[i], quantity=qty_list[i], total=tot_list[i], order_id=order.id, user_id=user.id)
			db.session.add(list)
			db.session.commit()
		return redirect (url_for('create_orders', company_name=company.company_name, order_no=order.order_no))
	if form.submit.data:
		order.order_submitted_by.append(user)
		order.date_submitted = datetime.utcnow()
		db.session.commit()
		return redirect (url_for('orders', company_name=company.company_name))
	form1 = EditOrderListForm()
	'''if form1.form_save_edit.data:
		order_edit = OrdersList.query.get(form.orderlist_id.data)
		order_edit.quantity = form1.edit_qty.data
		db.session.commit()
		return redirect (url_for('create_orders', company_name=company.company_name, order_no=order.order_no))'''
	return render_template('inventory_management/create_orders.html', title='Create Orders', user=user, company=company, products=products, my_products=my_products, order=order, is_super_admin=is_super_admin, is_my_affiliate=is_my_affiliate, order_list=order_list, form=form, dept=dept, form1=form1)	


@app.route('/<company_name>/<order_no>/remove_order_item/<int:id>')
@login_required	
def remove_order_item(company_name, order_no, id):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	order = Order.query.filter_by(order_no=order_no).first_or_404()
	#order_list = OrdersList.query.filter_by(order_id=order.id).all()
	item = OrdersList.query.filter_by(id=id).first()
	db.session.delete(item)
	db.session.commit()
	return redirect (url_for('create_orders', company_name=company.company_name, order_no=order.order_no))

#edit item from modal
#cannot get data from form
@app.route('/<company_name>/<order_no>/edit_item_qty/<int:id>', methods=['GET', 'POST'])
@login_required	
def edit_item_qty(company_name, order_no, id):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	order = Order.query.filter_by(order_no=order_no).first_or_404()
	#order_list = OrdersList.query.filter_by(order_id=order.id).all()
	item = OrdersList.query.filter_by(id=id).first()
	form1 = EditOrderListForm()
	order_id = form1.orderlist_id.data
	edit_qty = form1.edit_qty.data
	print(form1.edit_qty.data)
	return redirect (url_for('create_orders', company_name=company.company_name, order_no=order.order_no))
	
		
@app.route('/<company_name>/inventory_management/purchases', methods=['GET', 'POST'])
@login_required
def purchases(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	purchases = Purchase.query.filter_by(company_id=company.id).all()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	#form = CreatePurchaseOrderForm()
	#for purchase in purchases:
	#	purchase.purchase_created_by = User.query.filter_by(id=purchase.created_by).first().username
	return render_template('inventory_management/purchases.html', title='Purchases', user=user, company=company, purchases=purchases, is_my_affiliate=is_my_affiliate, is_super_admin=is_super_admin)		


@app.route('/<company_name>/inventory_management/purchase_list/<purchase_order_no>', methods=['GET', 'POST'])
@login_required
def purchase_list(company_name, purchase_order_no):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	purchase = Purchase.query.filter_by(purchase_order_no=purchase_order_no).first_or_404()
	purchase_list = PurchaseList.query.filter_by(purchase_id=purchase.id).all()
	for list in purchase_list:
		list.user = User.query.filter_by(id=list.user_id).first()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	dept = company.departments.order_by(Department.name.asc())
	my_products = MyProducts.query.all()
	for my_p in my_products:
		my_p.name = Product.query.filter_by(id=my_p.product_id).first().name
		my_p.ref_number = Product.query.filter_by(id=my_p.product_id).first().ref_number
		my_p.description = Product.query.filter_by(id=my_p.product_id).first().description
		my_p.department = Department.query.filter_by(id=my_p.department_id).first().name
	form = OrderListForm()
	if form.save.data:
		refnum_list = request.form.getlist('refnum')
		name_list = request.form.getlist('name')
		price_list = request.form.getlist('price')
		qty_list = request.form.getlist('qty')
		tot_list = request.form.getlist('tot_price')
		#for i in refnum_list, price_list in range(0, len(refnum_list) ):
		for i in range(0, len(refnum_list) ):
			#print(refnum_list[i], name_list[i])
		#for refnum_list, name_list, price_list, qty_list, tot_list in range(0, len(refnum_list)):
			list = PurchaseList(ref_number=refnum_list[i], name=name_list[i], price=price_list[i], quantity=qty_list[i], total=tot_list[i], purchase_id=purchase.id, user_id=user.id)
			db.session.add(list)
			db.session.commit()
		return redirect (url_for('purchase_list', company_name=company.company_name, purchase_order_no=purchase.purchase_order_no))
	if form.submit.data:
		purchase.purchased_by.append(user)
		purchase.date_purchased = datetime.utcnow()
		db.session.commit()
		return redirect (url_for('purchases', company_name=company.company_name))
	return render_template('inventory_management/purchase_list.html', title='Purchase List', user=user, company=company, purchase=purchase, is_my_affiliate=is_my_affiliate, is_super_admin=is_super_admin, purchase_list=purchase_list, form=form, dept=dept, my_products=my_products)		


@app.route('/<company_name>/<purchase_order_no>/remove_purchase_item/<int:id>')
@login_required	
def remove_purchase_item(company_name, purchase_order_no, id):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	purchase = Purchase.query.filter_by(purchase_order_no=purchase_order_no).first_or_404()
	item = PurchaseList.query.filter_by(id=id).first()
	db.session.delete(item)
	db.session.commit()
	return redirect (url_for('purchase_list', company_name=company.company_name, purchase_order_no=purchase.purchase_order_no))
	

@app.route('/<company_name>/<purchase_order_no>/accept_delivery/<delivery_order_no>')
@login_required	
def accept_delivery(company_name, purchase_order_no, delivery_order_no):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	purchase = Purchase.query.filter_by(purchase_order_no=purchase_order_no).first_or_404()
	purchase_list = PurchaseList.query.filter_by(purchase_id=purchase.id).all()
	for list in purchase_list:
		list.delivered_qty = Item.query.filter_by(purchase_list_id=list.id).count()
		list.complete_delivery = list.delivered_qty == list.quantity
		list.purchase_list_id = Item.query.filter_by(purchase_list_id=list.id).all()
		list.delivery_no_list = []
		for l in list.purchase_list_id:
			l.delivery_no = Delivery.query.filter_by(id=l.delivery_id).first().delivery_no
			list.delivery_no_list.append(l.delivery_no)
		list.count_delivery_no_list = dict((x,list.delivery_no_list.count(x)) for x in set(list.delivery_no_list))	
	delivery = Delivery.query.filter_by(delivery_no=delivery_order_no).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	return render_template('inventory_management/accept_delivery.html', title='Accept Delivery', user=user, company=company, purchase=purchase, is_my_affiliate=is_my_affiliate, is_super_admin=is_super_admin, purchase_list=purchase_list, delivery=delivery)		


@app.route('/<company_name>/<purchase_order_no>/receive_delivery_item/<delivery_order_no>/<int:id>', methods=['GET', 'POST'])
@login_required	
def receive_delivery_item(company_name, purchase_order_no, delivery_order_no, id):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	purchase = Purchase.query.filter_by(purchase_order_no=purchase_order_no).first_or_404()
	purchase_list = PurchaseList.query.filter_by(purchase_id=purchase.id).all()
	purchased_item = PurchaseList.query.filter_by(id=id).first()
	delivery = Delivery.query.filter_by(delivery_no=delivery_order_no).first_or_404()
	product = Product.query.filter_by(ref_number=purchased_item.ref_number).first()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	form = ItemReceiveForm()
	if form.validate_on_submit():
		raw_lotno = form.lot_no.data
		qty = form.quantity.data
		#form_expiry = form.expiry.data.split('-')
		#raw_expiry = datetime.strptime('form_expiry', '%Y-%m-%d')
		alnum_lotno = ''.join(e for e in raw_lotno if e.isalnum())
		lot_query = Lot.query.filter_by(lot_no=alnum_lotno).first()
		if lot_query is None:
			lot = Lot(lot_no=alnum_lotno, product_id=product.id, expiry=form.expiry.data)
			db.session.add(lot)
			db.session.commit()
			for i in range(0, qty):
				item = Item(lot_id=lot.id, company_id=company.id, product_id=product.id, purchase_list_id=id, delivery_id=delivery.id)
				db.session.add(item)
				db.session.commit()
			return redirect(url_for('accept_delivery', company_name=company.company_name, purchase_order_no=purchase.purchase_order_no, delivery_order_no=delivery.delivery_no))
		if lot_query is not None:
			lot = Lot.query.filter_by(lot_no=alnum_lotno).first()
			for i in range(0, qty):
				item = Item(lot_id=lot.id, company_id=company.id, product_id=product.id, purchase_list_id=id, delivery_id=delivery.id)
				db.session.add(item)
				db.session.commit()
			return redirect(url_for('accept_delivery', company_name=company.company_name, purchase_order_no=purchase_order_no, delivery_order_no=delivery_order_no))
	return render_template('inventory_management/receive_delivery_item.html', title='Receive Item', user=user, company=company, purchase=purchase, is_my_affiliate=is_my_affiliate, is_super_admin=is_super_admin, purchased_item=purchased_item, form=form, delivery=delivery)	

	
@app.route('/<company_name>/inventory_management/deliveries', methods=['GET', 'POST'])
@login_required
def deliveries(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	purchases = Purchase.query.filter_by(company_id=company.id).all()
	for purchase in purchases:
		purchase.delivered_purchases = Delivery.query.filter_by(purchase_id=purchase.id).all()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	form = AcceptDeliveryForm()
	if form.validate_on_submit():
		purchase = Purchase.query.filter_by(purchase_order_no=form.purchase_no.data).first_or_404()
		delivery = Delivery(delivery_no=form.delivery_no.data, receiver_id=user.id, company_id=company.id, purchase_id=purchase.id)
		db.session.add(delivery)
		db.session.commit()
		return redirect(url_for('accept_delivery', company_name=company.company_name, purchase_order_no=purchase.purchase_order_no, delivery_order_no=delivery.delivery_no))
	return render_template('inventory_management/deliveries.html', title='Deliveries', user=user, company=company, is_super_admin=is_super_admin, is_my_affiliate=is_my_affiliate, purchases=purchases, form=form)
	
@app.route('/<company_name>/inventory_management/suppliers',  methods=['GET', 'POST'])
@login_required
def suppliers(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	form = SupplierRegistrationForm()
	if form.validate_on_submit():
		supp = Supplier.query.filter_by(name=form.supplier_name.data).first()
		if supp is not None:
			company.suppliers.append(supp)
		else:
			supplier = Supplier(name=form.supplier_name.data, address=form.address.data, email=form.email.data, contact=form.contact.data)
			db.session.add(supplier)
			company.suppliers.append(supplier)
		db.session.commit()
		return redirect(url_for('suppliers', company_name=company.company_name))
	suppliers = Supplier.query.order_by(Supplier.name.asc()).all()
	return render_template('inventory_management/suppliers.html', title='Suppliers', user=user, form=form, suppliers=suppliers, company=company, is_super_admin=is_super_admin)



@app.route('/remove_supplier/<int:supp_id>, <int:comp_id>')	
@login_required	
def remove_supplier(supp_id, comp_id):
	company = Company.query.filter_by(id=comp_id).first_or_404()
	supplier = Supplier.query.get(supp_id)
	supplier.remove_company(company)
	db.session.commit()
	flash('Supplier has been removed.')
	return redirect(url_for('suppliers', company_name=company.company_name))


@app.route('/<company_name>/inventory_management/departments',  methods=['GET', 'POST'])
@login_required
def departments(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	form1 = DepartmentRegistrationForm()
	form2 = TypeRegistrationForm()
	if form1.validate_on_submit():
		dept = Department.query.filter_by(name=form1.dept_name.data).first()
		if dept is not None:
			company.departments.append(dept)
		else:
			department_name = Department(name=form1.dept_name.data)
			db.session.add(department_name)
			company.departments.append(department_name)
		db.session.commit()
		return redirect(url_for('departments', company_name=company.company_name))	
	if form2.validate_on_submit():
		type = Type.query.filter_by(name=form2.type_name.data).first()
		if type is not None:
			company.types.append(type)
		else:
			type_name = Type(name=form2.type_name.data)
			db.session.add(type_name)
			company.types.append(type_name)
		db.session.commit()
		return redirect(url_for('departments', company_name=company.company_name))	
	departments = Department.query.order_by(Department.name.asc()).all()
	types = Type.query.order_by(Type.name.asc()).all()
	return render_template('inventory_management/departments.html', title='Departments', user=user, form1=form1, form2=form2, types=types, company=company, is_super_admin=is_super_admin, departments=departments)

@app.route('/remove_dept/<int:dept_id>, <int:comp_id>')
@login_required
def remove_dept(dept_id, comp_id):
	company = Company.query.get(comp_id)
	dept = Department.query.get(dept_id)
	dept.remove_company(company)
	db.session.commit()
	flash('Department name removed.')
	return redirect(url_for('departments', company_name=company.company_name))
	
'''@app.route('/edit_dept/<int:id>, <int:comp_id>', methods=['GET', 'POST'])
def edit_dept(id, comp_id):
	company = Company.query.filter_by(id=comp_id).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_super_admin = company.is_super_admin(user)
	form1 = DepartmentEditForm()
	dept = Department.query.get(id)
	if form1.submit.data:
		if form1.validate_on_submit():
			dept.name = form1.dept_name.data
			db.session.commit()
			return redirect(url_for('departments', company_name=company.company_name))	
	elif request.method == 'GET':
		form1.dept_name.data = dept.name
	departments = Department.query.order_by(Department.name.asc()).all()
	return render_template('inventory_management/departments.html', title='Departments', form1=form1, departments=departments, is_super_admin=is_super_admin, company=company)'''

@app.route('/remove_type/<int:type_id>, <int:comp_id>', methods=['GET', 'POST'])
@login_required
def remove_type(type_id, comp_id):
	company = Company.query.get(comp_id)
	type = Type.query.get(type_id)
	type.remove_company(company)
	db.session.commit()
	flash('Type name deleted.')
	return redirect(url_for('departments', company_name=company.company_name))
	
'''@app.route('/edit_type/<int:id>, <int:comp_id>', methods=['GET', 'POST'])
def edit_type(id, comp_id):
	company = Company.query.filter_by(id=comp_id).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_super_admin = company.is_super_admin(user)
	form1 = TypeEditForm()
	type = Type.query.get(id)
	if form1.submit.data:
		if form1.validate_on_submit():
			type.name = form1.type_name.data
			db.session.commit()
			return redirect(url_for('departments', company_name=company.company_name))	
	elif request.method == 'GET':
		form1.type_name.data = type.name
	types = Type.query.order_by(Type.name.asc()).all()
	return render_template('inventory_management/departments.html', title='Departments', form1=form1, types=types, is_super_admin=is_super_admin, company=company)'''
	

	


'''@app.route('/orders_list', methods=['GET', 'POST'])	
def orders_list():
	order_list = OrdersList.query.all()
	for order in order_list:
		order.ref_no = Product.query.filter_by(id=order_list.prod_id).first().ref_number
		order.product_code = Product.query.filter_by(id=order_list.prod_id).first().product_code
		order.name = Product.query.filter_by(id=order_list.prod_id).first().name
		order.price = Product.query.filter_by(id=order_list.prod_id).first().price
	return render_template('inventory_management/create_orders.html', order_list=order_list)'''

@app.route('/document_control/<username>')
@login_required
def document_control(username):
	form = DocumentRequestForm()
	user = User.query.filter_by(username=username).first_or_404()
	return render_template('document_control.html', title='Document Control', user=user, form=form)
	
@app.route('/document_control_sample')
def document_control_sample():
	return render_template('document_control_sample.html', title='Document Control')
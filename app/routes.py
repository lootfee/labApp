from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from flask_cors import CORS, cross_origin
from werkzeug.urls import url_parse
from app import app, db, photos
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm, ProductRegistrationForm, DepartmentRegistrationForm, DepartmentEditForm, TypeRegistrationForm, TypeEditForm, SupplierRegistrationForm, InventorySearchForm, CompanyRegistrationForm, CompanyProfileForm, UserRoleForm, CreateOrderIDForm, OrderListForm, EditOrderListForm, CreatePurchaseOrderForm, ItemReceiveForm, AcceptDeliveryForm, ConsumeItemForm, CommentForm, MessageForm, CreateDocumentForm, MessageFormDirect, CreateDocumentSectionForm, EditDocumentBodyForm
from app.models import User, Post, Product, Item, Department, Supplier, Type, Order, Company, Affiliates, MyProducts, OrdersList, Purchase, PurchaseList, Delivery, Item, Lot, Comment, CommentReply, Message, DocumentName, DocumentationDepartment, DocumentSection, DocumentSectionBody, DocumentVersion
from datetime import datetime, timedelta
from app.email import send_password_reset_email
from link_preview import link_preview
import requests
import markdown2 

# TO DO
# - reaffiliate/rehire code
# - remove accepted from affiliates, change to start_date
# - improve user search algo
# - verify reset password

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
	companies = Company.query.order_by(Company.company_name.desc()).all()
	users = User.query.order_by(User.username.desc()).all()
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
	return render_template('index.html', title='Home', form=form, posts=posts.items, next_url=next_url, prev_url=prev_url, user=user, companies=companies, users=users)

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
	companies = Company.query.order_by(Company.company_name.desc()).all()
	users = User.query.order_by(User.username.desc()).all()
	page = request.args.get('page', 1, type=int)
	form = CompanyRegistrationForm()
	if form.validate_on_submit():
		company = Company(company_name=form.company_name.data, user_id=current_user.id)
		db.session.add(company)
		db.session.commit()
		accept = Affiliates(super_admin=True, start_date=datetime.utcnow())
		accept.user_id = current_user.id
		company.affiliate.append(accept)
		db.session.commit()
		return redirect(url_for('company', company_name=company.company_name))
	my_affiliates = Affiliates.query.filter(Affiliates.start_date.isnot(None)).filter_by(user_id=user.id).all()
	#for affiliate in my_affiliates:
	#	affiliate.comp_id = affiliate.company_id
		#affiliate.company = Company.query.filter_by(id=affiliate.company_id).first()
	posts = user.posts.order_by(Post.timestamp.desc()).paginate(
		page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
	prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
	return render_template('user.html', title=user.username, user=user, posts=posts.items, prev_url=prev_url, next_url=next_url, form=form, my_affiliates=my_affiliates, companies=companies, users=users)
		

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	user = User.query.filter_by(username=current_user.username).first_or_404()
	companies = Company.query.order_by(Company.company_name.desc()).all()
	users = User.query.order_by(User.username.desc()).all()
	form = EditProfileForm(current_user.username)
	if form.submit.data:
		if form.validate_on_submit():
			current_user.firstname = form.firstname.data
			current_user.lastname = form.lastname.data
			current_user.username = form.username.data
			current_user.about_me = form.about_me.data
			current_user.email = form.email.data
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
		form.email.data = current_user.email
	return render_template('edit_profile.html', title='Edit Profile', form=form, user=user, companies=companies, users=users)
	
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
@login_required
@cross_origin()
def explore():
	user = User.query.filter_by(username=current_user.username).first()
	companies = Company.query.order_by(Company.company_name.desc()).all()
	users = User.query.order_by(User.username.desc()).all()
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.timestamp.desc()).paginate(
		page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('explore', page=posts.next_num) \
		if posts.has_next else None
	prev_url = url_for('explore', page=posts.prev_num) \
		if posts.has_prev else None
	return render_template('index.html', title='Global', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url, companies=companies, users=users)


@app.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def post(id):
	user = User.query.filter_by(username=current_user.username).first()
	companies = Company.query.order_by(Company.company_name.desc()).all()
	users = User.query.order_by(User.username.desc()).all()
	post = Post.query.filter_by(id=id).first_or_404()
	upvotes = post.upvoters.count()
	downvotes = post.downvoters.count()
	upvoted = post.upvoted(user)
	downvoted = post.downvoted(user)
	form = CommentForm()
	if form.validate_on_submit():
		comment = Comment(body=form.comment.data, user_id=user.id, post_id=post.id)
		db.session.add(comment)
		db.session.commit()
		return redirect(url_for('post', id=post.id))
	comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.timestamp.desc()).all()
	return render_template('post.html', title='Post', user=user, post=post, upvotes=upvotes, downvotes=downvotes, upvoted=upvoted, downvoted=downvoted, form=form, comments=comments, companies=companies, users=users)
	

@app.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
	user_recipient = User.query.filter_by(username=recipient).first_or_404()
	companies = Company.query.order_by(Company.company_name.desc()).all()
	users = User.query.order_by(User.username.desc()).all()
	form = MessageFormDirect()
	if form.validate_on_submit():
		msg = Message(author=current_user, recipient=user_recipient, body=form.message.data)
		db.session.add(msg)
		db.session.commit()
		flash(('Your message has been sent.'))
		return redirect(url_for('user', username=recipient))
	return render_template('send_message.html', title=('Send Message'), form=form, user_recipient=user_recipient, companies=companies, users=users)

@app.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
	companies = Company.query.order_by(Company.company_name.desc()).all()
	users = User.query.order_by(User.username.desc()).all()
	current_user.last_message_read_time = datetime.utcnow()
	db.session.commit()
	#page = request.args.get('page', 1, type=int)
	received_messages = current_user.messages_received.order_by( Message.timestamp.desc())
	sent_messages = current_user.messages_sent.order_by( Message.timestamp.desc())
	form = MessageForm()
	if form.validate_on_submit():
		user_recipient = User.query.filter_by(username=form.user_search_bar.data).first_or_404()
		msg = Message(author=current_user, recipient=user_recipient, body=form.message.data)
		db.session.add(msg)
		db.session.commit()
		flash(('Your message has been sent.'))
		return redirect(url_for('messages'))
	return render_template('messages.html', received_messages=received_messages, sent_messages=sent_messages, companies=companies, users=users, form=form)

	
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
	companies = Company.query.order_by(Company.company_name.desc()).all()
	users = User.query.order_by(User.username.desc()).all()
	affiliates = Affiliates.query.filter_by(company_id=company.id, accepted=True, end_date=None).all()
	pending_affiliates = Affiliates.query.filter_by(company_id=company.id, start_date=None).all()
	is_my_affiliate = company.is_my_affiliate(user)
	is_pending_affiliate = company.is_pending_affiliate(user)
	is_super_admin = company.is_super_admin(user)
	form = CompanyProfileForm()
	if form.submit.data:
		if form.validate_on_submit():
			company.company_name = form.company_name.data
			company.company_abbrv = form.company_abbrv.data
			company.about_me = form.about_me.data
			company.email = form.email.data
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
		form.company_abbrv.data = company.company_abbrv
		if company.email:
			form.email.data = company.email
		if company.about_me:
			form.about_me.data = company.about_me
		if company.address:
			form.address.data = company.address
		if company.logo:
			form.logo.data = company.logo
		if company.contact_info:
			form.contact_info.data = company.contact_info
	return render_template('company.html', form=form, company=company, user=user, affiliates=affiliates, pending_affiliates=pending_affiliates,  is_my_affiliate=is_my_affiliate, is_pending_affiliate=is_pending_affiliate, is_super_admin=is_super_admin, companies=companies, users=users)

@app.route('/accept_affiliate/<int:user_id>, <int:comp_id>')
@login_required
def accept_affiliate(user_id, comp_id):
	company = Company.query.filter_by(id=comp_id).first_or_404()
	pending_affiliate = Affiliates.query.filter_by(user_id=user_id, company_id=comp_id, start_date=None).first()
	#user = User.query.filter_by(username=current_user.username).first_or_404()
	#if user.id == pending_affiliate.user_id:
	#pending_affiliate.accepted = True
	pending_affiliate.start_date = datetime.utcnow()
	db.session.commit()
	return redirect(url_for('admin', company_name=company.company_name))
	
@app.route('/retire_affiliate/<int:user_id>, <int:comp_id>')
@login_required
def retire_affiliate(user_id, comp_id):
	company = Company.query.filter_by(id=comp_id).first_or_404()
	#user = User.query.filter(id==user_id).first_or_404()
	affiliate = Affiliates.query.filter_by(user_id=user_id, company_id=comp_id).first()
	affiliate.end_date = datetime.utcnow()
	affiliate.inv_supervisor = False
	affiliate.inv_admin = False
	affiliate.qc_supervisor = False
	affiliate.qc_admin = False
	affiliate.doc_supervisor = False
	affiliate.doc_admin = False
	affiliate.super_admin = False
	db.session.commit()
	return redirect(url_for('admin', company_name=company.company_name))
	
@app.route('/delete_affiliate/<int:user_id>, <int:comp_id>')
@login_required
def delete_affiliate(user_id, comp_id):
	company = Company.query.filter_by(id=comp_id).first_or_404()
	#user = User.query.filter(id==user_id).first_or_404()
	affiliate = Affiliates.query.filter_by(user_id=user_id, company_id=comp_id).all()
	company.remove_affiliate(affiliate)
	#db.session.delete(aff)
	db.session.commit()
	return redirect(url_for('admin', company_name=company.company_name))

@app.route('/manage_affiliate/<int:user_id>, <int:comp_id>', methods=['GET', 'POST'])
@login_required
def manage_affiliate(user_id, comp_id):
	company = Company.query.filter_by(id=comp_id).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	affiliate = Affiliates.query.filter(Affiliates.start_date.isnot(None)).filter_by(user_id=user_id, company_id=comp_id, end_date=None).first()
	is_super_admin = company.is_super_admin(user)
	if not is_super_admin:
		return redirect(url_for('company', company_name=company.company_name))
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	form = UserRoleForm()
	if form.submit.data:
		if form.validate_on_submit():
			affiliate.title = form.title.data
			#affiliate.qc_supervisor = form.qc_supervisor.data
			affiliate.inv_supervisor = form.inv_supervisor.data
			affiliate.doc_supervisor = form.doc_supervisor.data
			#affiliate.qc_admin = form.qc_admin.data
			affiliate.inv_admin = form.inv_admin.data
			affiliate.doc_admin = form.doc_admin.data
			affiliate.super_admin = form.super_admin.data
			#if form.qc_admin.data:
			#	affiliate.qc_supervisor = True
			if form.inv_admin.data:
				affiliate.inv_supervisor = True
			if form.doc_admin.data:
				affiliate.doc_supervisor = True
			if form.super_admin.data:
				#affiliate.qc_supervisor = True
				affiliate.inv_supervisor = True
				affiliate.doc_supervisor = True
				#affiliate.qc_admin = True
				affiliate.inv_admin = True
				affiliate.doc_admin = True
			db.session.commit()
			flash('Your changes has been saved!')
			return redirect(url_for('admin', company_name=company.company_name))
	elif request.method == 'GET':
		form.title.data = affiliate.title
		#form.qc_supervisor.data = affiliate.qc_supervisor
		form.inv_supervisor.data = affiliate.inv_supervisor
		form.doc_supervisor.data = affiliate.doc_supervisor
		#form.qc_admin.data = affiliate.qc_admin
		form.inv_admin.data = affiliate.inv_admin
		form.doc_admin.data = affiliate.doc_admin
		form.super_admin.data = affiliate.super_admin
	return render_template('manage_affiliate_role.html', user=user, form=form, company=company, affiliate=affiliate, is_my_affiliate=is_my_affiliate, is_super_admin=is_super_admin)

@app.route('/request_affiliate/<company_name>', methods=['GET', 'POST'])
@login_required
def request_affiliate(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user_query = Affiliates.query.filter_by(user_id=current_user.id, company_id=company.id).first()
	if user_query is None:
		request = Affiliates(user_id=current_user.id, company_id=company.id)
		company.affiliate.append(request)
		db.session.commit()
		flash('Affiliate request sent!')
	else:
		flash('You already have sent a request or is affiliated to the company!')
	return redirect(url_for('company', company_name=company.company_name))
	
	
@app.route('/admin/<company_name>', methods=['GET', 'POST'])
@login_required
def admin(company_name):
	form = UserRoleForm()
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	affiliates = Affiliates.query.filter(Affiliates.start_date.isnot(None)).filter_by(company_id=company.id, end_date=None).all()
	#for affiliate in affiliates:
	#	affiliate.this_affiliate = affiliate.users.username
	#	this_aff = affiliate.this_affiliate
	pending_affiliates = Affiliates.query.filter_by(company_id=company.id, start_date=None).all()
	past_affiliates = Affiliates.query.filter(Affiliates.end_date.isnot(None), Affiliates.start_date.isnot(None)).filter_by(company_id=company.id).order_by(Affiliates.start_date.desc()).all()
	is_super_admin = company.is_super_admin(user)
	if not is_super_admin:
		return redirect(url_for('company', company_name=company.company_name))
	is_my_affiliate = company.is_my_affiliate(user)
	if is_my_affiliate:
		return render_template('admin.html', title='Admin', user=user, form=form, company=company, affiliates=affiliates, pending_affiliates=pending_affiliates, past_affiliates=past_affiliates, is_my_affiliate=is_my_affiliate, is_super_admin=is_super_admin)
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

@app.route('/quality_control_')
def quality_control_sample():
	return render_template('quality_control_sample.html', title='Quality Control')
	
@app.route('/inventory_management_')	
def inventory_management_sample():
	return render_template('inventory_management/inventory_overview_sample.html', title='Inventory Overview')
	
@app.route('/<company_name>/inventory_management/overview', methods=['GET', 'POST'])	
@login_required
def inventory_management(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	select_dept = company.departments.order_by(Department.name.asc())
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	my_products = MyProducts.query.filter_by(company_id=company.id).all()
	for my_p in my_products:
		my_p.name = Product.query.filter_by(id=my_p.product_id).first().name
		my_p.ref_number = Product.query.filter_by(id=my_p.product_id).first().ref_number
		my_p.description = Product.query.filter_by(id=my_p.product_id).first().description
		my_p.storage_req = Product.query.filter_by(id=my_p.product_id).first().storage_req
		my_p.min_quantity = MyProducts.query.filter_by(product_id=my_p.product_id).first().min_quantity
		my_p.current_quantity = Item.query.filter_by(product_id=my_p.product_id, date_used=None).count()
		my_p.less_quantity = my_p.min_quantity >= my_p.current_quantity
		my_p.min_expiry = MyProducts.query.filter_by(product_id=my_p.product_id).first().min_expiry
		my_p.dept_name = Department.query.filter_by(id=my_p.department_id).first().name
		my_p.type_name = Type.query.filter_by(id=my_p.type_id).first().name
		my_p.supplier_name = Supplier.query.filter_by(id=my_p.supplier_id).first().name
		my_p.item_query = Item.query.filter_by(product_id=my_p.product_id, date_used=None).all()
		for i in my_p.item_query:
			i.lot_num = Lot.query.filter_by(id=i.lot_id).first().lot_no
			i.expiry = Lot.query.filter_by(id=i.lot_id).first().expiry
			i.min_expiry = datetime.utcnow() + timedelta(days=my_p.min_expiry)
			i.greater_expiry =  (i.expiry < i.min_expiry)
	pending_deliveries = Purchase.query.filter(Purchase.date_purchased.isnot(None)).filter_by(company_id=company.id, purchase_to_delivery=None).all()
	delivered_purchases = Delivery.query.filter_by(company_id=company.id).all()
	pending_item = []
	for dp in delivered_purchases:
		dp.purchase_list = PurchaseList.query.filter_by(company_id=company.id, purchase_id=dp.purchase_id).all()
		for pl in dp.purchase_list:
			pl.name = PurchaseList.query.filter_by(id=pl.id).first().name
			pl.ref_number = PurchaseList.query.filter_by(id=pl.id).first().ref_number
			pl.purchase_order_no = Purchase.query.filter_by(company_id=company.id, id=pl.purchase_id).first().purchase_order_no
			pl.date_purchased = Purchase.query.filter_by(company_id=company.id, id=pl.purchase_id).first().date_purchased
			pl.qty = PurchaseList.query.filter_by(company_id=company.id, purchase_id=dp.purchase_id, id=pl.id).first().quantity
			pl.delivered_qty = Item.query.filter_by(purchase_list_id=pl.id).count()
			pl.product_id = Product.query.filter_by(ref_number=pl.ref_number).first().id
			pl.dept_id = MyProducts.query.filter_by(company_id=company.id, product_id=pl.product_id).first().department_id
			pl.dept_name = Department.query.filter_by(id=pl.dept_id).first().name
	unsubmitted_orders = Order.query.filter(Order.date_submitted.isnot(None)).filter_by(puchase_no=None, company_id=company.id).all()
	pending_purchases = Purchase.query.filter_by(company_id=company.id, date_purchased=None).all()
	return render_template('inventory_management/inventory_overview.html', title='Inventory Overview', company=company, is_super_admin=is_super_admin, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor, my_products=my_products, unsubmitted_orders=unsubmitted_orders, pending_purchases=pending_purchases, purchases=purchases, pending_deliveries=pending_deliveries, delivered_purchases=delivered_purchases, select_dept=select_dept)	


@app.route('/<company_name>/inventory_management/products', methods=['GET', 'POST'])
@login_required
def products(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	select_dept = company.departments.order_by(Department.name.asc())
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
			my_prod = MyProducts.query.filter_by(product_id=prod.id, company_id=company.id).first()
			if my_prod:
				flash('Product already registered, if you wish to edit, delete the product and register again.')
			else:
				p = MyProducts(company_id=company.id, product_id=prod.id, price=form.price.data, min_expiry=form.min_expiry.data, min_quantity=form.min_quantity.data, department_id=form.department.data, type_id=form.type.data, supplier_id=form.supplier.data, user_id=current_user.id)
				db.session.add(p)
				db.session.commit()
			return redirect(url_for('products', company_name=company.company_name))	
		else:
			product = Product(ref_number=alnum_refnum, name=form.name.data, description=form.description.data, storage_req=form.storage_req.data, user_id=current_user.id)
			db.session.add(product)
			db.session.commit()
			p = MyProducts(company_id=company.id, product_id=product.id, price=form.price.data, min_expiry=form.min_expiry.data, min_quantity=form.min_quantity.data, department_id=form.department.data, type_id=form.type.data, supplier_id=form.supplier.data, user_id=current_user.id)
			db.session.add(p)
			db.session.commit()
		return redirect(url_for('products', company_name=company.company_name))
	products = Product.query.order_by(Product.name.asc()).all()
	my_products = MyProducts.query.filter_by(company_id=company.id).all()
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
	return render_template('inventory_management/products.html', title='Manage Products', user=user, form=form, products=products, company=company, is_super_admin=is_super_admin, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor, my_products=my_products, select_dept=select_dept)

@app.route('/edit_my_product/<int:prod_id>, <int:comp_id>')	
@login_required	
def edit_my_product(prod_id, comp_id):
	my_product = MyProducts.query.filter_by(product_id=prod_id, company_id=comp_id).first()
	product = Product.query.filter_by(id=prod_id).first()
	company = Company.query.filter_by(id=comp_id).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
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
		my_product.price = form.price.data
		my_product.min_expiry = form.min_expiry.data
		my_product.min_quantity = form.min_quantity.data
		my_product.department_id = form.department.data
		my_product.type_id = form.type.data
		my_product.supplier_id = form.supplier.data
		db.session.commit()
		return redirect(url_for('products', company_name=company.company_name))	
	elif request.method == 'GET':
		form.price.data = my_product.price
		form.min_expiry.data = my_product.min_expiry
		form.min_quantity.data = my_product.min_quantity
		form.department.data = my_product.department_id
		form.type.data = my_product.type_id
		form.supplier.data = my_product.supplier_id
	return render_template('inventory_management/edit_product.html', title='Edit Products', user=user, form=form, product=product, company=company, is_super_admin=is_super_admin, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor)
	

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
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	dept = company.departments.order_by(Department.name.asc())
	products = Product.query.order_by(Product.name.asc())
	my_products = MyProducts.query.filter_by(company_id=company.id).all()
	for my_p in my_products:
		my_p.name = Product.query.filter_by(id=my_p.product_id).first().name
		my_p.ref_number = Product.query.filter_by(id=my_p.product_id).first().ref_number
		my_p.description = Product.query.filter_by(id=my_p.product_id).first().description
		my_p.dept = Department.query.filter_by(id=my_p.department_id).first().name
		#my_p.stocks = Item.query.filter_by(product_id=my_p.product_id, date_used=None).count()
		my_p.min_quantity = MyProducts.query.filter_by(product_id=my_p.product_id, company_id=company.id).first().min_quantity
		my_p.min_expiry = MyProducts.query.filter_by(product_id=my_p.product_id, company_id=company.id).first().min_expiry
		my_p.item_query = Item.query.filter_by(product_id=my_p.product_id, company_id=company.id, date_used=None).all()
		#my_p.lot_list = []
		for i in my_p.item_query:
			i.lot_num = Lot.query.filter_by(id=i.lot_id).first().lot_no
			i.expiry = Lot.query.filter_by(id=i.lot_id).first().expiry
			i.quantity = Item.query.filter_by(lot_id=i.lot_id, product_id=my_p.product_id, company_id=company.id, date_used=None).count()
			i.min_expiry = datetime.utcnow() + timedelta(days=my_p.min_expiry)
			i.greater_expiry =  (i.expiry < i.min_expiry)
			i.received_date = Delivery.query.filter_by(id=i.delivery_id).first().date_delivered
	return render_template('inventory_management/inventory.html', title='Inventory', user=user, company=company, is_super_admin=is_super_admin, is_my_affiliate=is_my_affiliate, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor, my_products=my_products, orders=orders, dept=dept)

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
	min_expiry = MyProducts.query.filter_by(product_id=product.id, company_id=company.id).first().min_expiry
	#product_id = Product.query.filter_by(ref_number=ref_number).first().id
	item_query = Item.query.filter_by(product_id=product.id, company_id=company.id, date_used=None).all()
	for i in item_query:
		i.lot_num = Lot.query.filter_by(id=i.lot_id).first().lot_no
		i.expiry = Lot.query.filter_by(id=i.lot_id).first().expiry
		i.datas = str(i.lot_num) + " - " + str(i.id) +  " / " + str(i.expiry.strftime('%d-%m-%Y'))
	form = ConsumeItemForm()
	lot_list = [(i.id, i.datas) for i in item_query]
	form.lot_numbers.choices = lot_list
	if form.validate_on_submit():
		#lot_num_id = Lot.query.filter_by(id=form.lot_numbers.data).first()
		use_item = Item.query.filter_by(product_id=product.id, company_id=company.id, id=form.lot_numbers.data, date_used=None).first()
		use_item.date_used = datetime.utcnow()
		use_item.user_id = current_user.id
		db.session.commit()
		return redirect(url_for('inventory', company_name=company.company_name))
	return render_template('inventory_management/consume.html', title='Consume supply', user=user, company=company, is_super_admin=is_super_admin, is_my_affiliate=is_my_affiliate, product=product, item_query=item_query, form=form)

@app.route('/<company_name>/inventory_management/orders', methods=['GET', 'POST'])
@login_required
def orders(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	orders = Order.query.filter_by(company_id=company.id).order_by(Order.date_created.desc()).all()
	for order in orders:
		order.purchase_order = Purchase.query.filter_by(order_no=order.id, company_id=company.id).first()
	purchases = Purchase.query.filter_by(company_id=company.id).all()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	form = CreateOrderIDForm()
	dept = company.departments
	dept_list = [(d.id, d.name) for d in dept]
	form.department.choices = dept_list
	form1 = CreatePurchaseOrderForm()
	if form.validate_on_submit():
		dept = Department.query.filter_by(id=form.department.data).first()
		order_n = company.company_abbrv + "-ORD-" + dept.abbrv + "-" + datetime.utcnow().strftime('%Y-%m-%d-%H%M%S')
		order = Order(order_no=order_n, company_id=company.id, department_id=dept.id)
		db.session.add(order)
		order.order_creator.append(user)
		db.session.commit()
		return redirect (url_for('create_orders', company_name=company.company_name, order_no=order.order_no))
	if form1.validate_on_submit():
		order_id = Order.query.filter_by(order_no=form1.order_no_purchase_form.data, company_id=company.id).first().id
		purchase = Purchase(purchase_order_no=form1.purchase_order.data, company_id=company.id, order_no=order_id)
		db.session.add(purchase)
		purchase.purchase_created_by.append(user)
		db.session.commit()
		purchase_list = OrdersList.query.filter_by(order_id=order_id, company_id=company.id).all()
		for i in purchase_list:
			list = PurchaseList(ref_number=i.ref_number, name=i.name, price=i.price, quantity=i.quantity, total=i.total, purchase_id=purchase.id, user_id=i.user_id, company_id=company.id)
			db.session.add(list)
			db.session.commit()
		return redirect (url_for('purchases', company_name=company.company_name))
	return render_template('inventory_management/orders.html', title='Orders', user=user, company=company, form=form, form1=form1, orders=orders, is_my_affiliate=is_my_affiliate, is_super_admin=is_super_admin, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor, purchases=purchases)



@app.route('/<company_name>/inventory_management/create_orders/<order_no>', methods=['GET', 'POST'])
@login_required
def create_orders(company_name, order_no):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	order = Order.query.filter_by(order_no=order_no, company_id=company.id).first_or_404()
	order_list = OrdersList.query.filter_by(order_id=order.id, company_id=company.id).all()
	for list in order_list:
		list.user = User.query.filter_by(id=list.user_id).first()
		list.supplier = Supplier.query.filter_by(id=list.supplier_id).first().name
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	dept = company.departments.order_by(Department.name.asc())
	products = Product.query.order_by(Product.name.asc())
	my_products = MyProducts.query.filter_by(company_id=company.id).all()
	for my_p in my_products:
		my_p.name = Product.query.filter_by(id=my_p.product_id).first().name
		my_p.ref_number = Product.query.filter_by(id=my_p.product_id).first().ref_number
		my_p.description = Product.query.filter_by(id=my_p.product_id).first().description
		my_p.department = Department.query.filter_by(id=my_p.department_id).first().name
		my_p.supplier = Supplier.query.filter_by(id=my_p.supplier_id).first().name
		my_p.item_count = Item.query.filter_by(product_id=my_p.product_id, company_id=company.id, date_used=None).count()
	form = OrderListForm()
	if form.save.data:
		refnum_list = request.form.getlist('refnum')
		name_list = request.form.getlist('name')
		qty_list = request.form.getlist('qty')
		supplier_list = request.form.getlist('supplier')
		for i in range(0, len(refnum_list) ):
			list = OrdersList(ref_number=refnum_list[i], name=name_list[i], quantity=qty_list[i], supplier=supplier_list[i],order_id=order.id, user_id=user.id, company_id=company.id)
			db.session.add(list)
			db.session.commit()
		return redirect (url_for('create_orders', company_name=company.company_name, order_no=order.order_no))
	if form.submit.data:
		order.order_submitted_by.append(user)
		order.date_submitted = datetime.utcnow()
		db.session.commit()
		return redirect (url_for('orders', company_name=company.company_name))
	return render_template('inventory_management/create_orders.html', title='Create Orders', user=user, company=company, products=products, my_products=my_products, order=order, is_super_admin=is_super_admin, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor, is_my_affiliate=is_my_affiliate, order_list=order_list, form=form, dept=dept)	


@app.route('/<company_name>/<order_no>/remove_order_item/<int:id>')
@login_required	
def remove_order_item(company_name, order_no, id):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	order = Order.query.filter_by(order_no=order_no, company_id=company.id).first_or_404()
	#order_list = OrdersList.query.filter_by(order_id=order.id).all()
	item = OrdersList.query.filter_by(id=id, company_id=company.id).first()
	db.session.delete(item)
	db.session.commit()
	return redirect (url_for('create_orders', company_name=company.company_name, order_no=order.order_no))

#edit item from modal
#cannot get data from form
@app.route('/<company_name>/<order_no>/edit_item_qty/<int:id>', methods=['GET', 'POST'])
@login_required	
def edit_item_qty(company_name, order_no, id):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	order = Order.query.filter_by(order_no=order_no, company_id=company.id).first_or_404()
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
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	is_inv_admin = company.is_inv_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	purchases = Purchase.query.filter_by(company_id=company.id).order_by(Purchase.date_created.desc()).all()
	for purchase in purchases:
		purchase.delivered_purchases = Delivery.query.filter_by(purchase_id=purchase.id, company_id=company.id).all()
		purchase.purchase_list = PurchaseList.query.filter_by(purchase_id=purchase.id, company_id=company.id).all()
		purchase.purchase_order_complete = False
		completed_item = 0
		for list in purchase.purchase_list:
			list.delivered_qty = Item.query.filter_by(purchase_list_id=list.id, company_id=company.id).count()
			list.complete_item_delivery = list.delivered_qty == list.quantity
		for n in range(0, len(purchase.purchase_list)):
			if list.complete_item_delivery:
				completed_item += 1
		if len(purchase.purchase_list) == completed_item:
			purchase.purchase_order_complete = True
	#form = CreatePurchaseOrderForm()
	#for purchase in purchases:
	#	purchase.purchase_created_by = User.query.filter_by(id=purchase.created_by).first().username
	return render_template('inventory_management/purchases.html', title='Purchases', user=user, company=company, purchases=purchases, is_my_affiliate=is_my_affiliate, is_super_admin=is_super_admin, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor)		


@app.route('/<company_name>/inventory_management/purchase_list/<purchase_order_no>', methods=['GET', 'POST'])
@login_required
def purchase_list(company_name, purchase_order_no):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	purchase = Purchase.query.filter_by(purchase_order_no=purchase_order_no, company_id=company.id).first_or_404()
	purchase_list = PurchaseList.query.filter_by(purchase_id=purchase.id, company_id=company.id).all()
	for list in purchase_list:
		list.user = User.query.filter_by(id=list.user_id).first()
		list.product_id = Product.query.filter_by(ref_number=list.ref_number).first().id
		list.supplier = Supplier.query.filter_by(id=list.supplier_id).first().name
		list.pricee = MyProducts.query.filter_by(company_id=company.id, product_id=list.product_id).first().price
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	is_inv_admin = company.is_inv_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	dept = company.departments.order_by(Department.name.asc())
	my_products = MyProducts.query.filter_by(company_id=company.id).all()
	for my_p in my_products:
		my_p.name = Product.query.filter_by(id=my_p.product_id).first().name
		my_p.ref_number = Product.query.filter_by(id=my_p.product_id).first().ref_number
		my_p.description = Product.query.filter_by(id=my_p.product_id).first().description
		my_p.department = Department.query.filter_by(id=my_p.department_id).first().name
		my_p.supplier = Supplier.query.filter_by(id=my_p.supplier_id).first().name
		my_p.item_count = Item.query.filter_by(product_id=my_p.product_id, company_id=company.id, date_used=None).count()
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
			list = PurchaseList(ref_number=refnum_list[i], name=name_list[i], price=price_list[i], quantity=qty_list[i], total=tot_list[i], purchase_id=purchase.id, user_id=user.id, company_id=company.id)
			db.session.add(list)
			db.session.commit()
		return redirect (url_for('purchase_list', company_name=company.company_name, purchase_order_no=purchase.purchase_order_no))
	if form.submit.data:
		purchase.purchased_by.append(user)
		purchase.date_purchased = datetime.utcnow()
		db.session.commit()
		return redirect (url_for('purchases', company_name=company.company_name))
	return render_template('inventory_management/purchase_list.html', title='Purchase List', user=user, company=company, purchase=purchase, is_my_affiliate=is_my_affiliate, is_super_admin=is_super_admin, is_inv_supervisor=is_inv_supervisor, is_inv_admin=is_inv_admin, purchase_list=purchase_list, form=form, dept=dept, my_products=my_products)		


@app.route('/<company_name>/<purchase_order_no>/remove_purchase_item/<int:id>')
@login_required	
def remove_purchase_item(company_name, purchase_order_no, id):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	purchase = Purchase.query.filter_by(purchase_order_no=purchase_order_no, company_id=company.id).first_or_404()
	item = PurchaseList.query.filter_by(id=id, company_id=company.id).first()
	db.session.delete(item)
	db.session.commit()
	return redirect (url_for('purchase_list', company_name=company.company_name, purchase_order_no=purchase.purchase_order_no))
	

@app.route('/<company_name>/<purchase_order_no>/accept_delivery/<delivery_order_no>')
@login_required	
def accept_delivery(company_name, purchase_order_no, delivery_order_no):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	purchase = Purchase.query.filter_by(purchase_order_no=purchase_order_no, company_id=company.id).first_or_404()
	purchase_list = PurchaseList.query.filter_by(purchase_id=purchase.id, company_id=company.id).all()
	for list in purchase_list:
		list.delivered_qty = Item.query.filter_by(purchase_list_id=list.id, company_id=company.id).count()
		list.complete_delivery = list.delivered_qty == list.quantity
		list.purchase_list_id = Item.query.filter_by(purchase_list_id=list.id, company_id=company.id).all()
		list.delivery_no_list = []
		for l in list.purchase_list_id:
			l.delivery_no = Delivery.query.filter_by(id=l.delivery_id, company_id=company.id).first().delivery_no
			list.delivery_no_list.append(l.delivery_no)
		list.count_delivery_no_list = dict((x,list.delivery_no_list.count(x)) for x in set(list.delivery_no_list))	
	delivery = Delivery.query.filter_by(delivery_no=delivery_order_no, company_id=company.id).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	is_inv_admin = company.is_inv_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	return render_template('inventory_management/accept_delivery.html', title='Accept Delivery', user=user, company=company, purchase=purchase, is_my_affiliate=is_my_affiliate, is_super_admin=is_super_admin, is_inv_supervisor=is_inv_supervisor, is_inv_admin=is_inv_admin, purchase_list=purchase_list, delivery=delivery)		


@app.route('/<company_name>/<purchase_order_no>/receive_delivery_item/<delivery_order_no>/<int:id>', methods=['GET', 'POST'])
@login_required	
def receive_delivery_item(company_name, purchase_order_no, delivery_order_no, id):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	purchase = Purchase.query.filter_by(purchase_order_no=purchase_order_no, company_id=company.id).first_or_404()
	#purchase_list = PurchaseList.query.filter_by(purchase_id=purchase.id, company_id=company.id).all()
	purchased_item = PurchaseList.query.filter_by(id=id, company_id=company.id).first()
	delivery = Delivery.query.filter_by(delivery_no=delivery_order_no, company_id=company.id).first_or_404()
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
				purchased_item.deliveries.append(delivery)
				db.session.commit()
			return redirect(url_for('accept_delivery', company_name=company.company_name, purchase_order_no=purchase.purchase_order_no, delivery_order_no=delivery.delivery_no))
		if lot_query is not None:
			lot = Lot.query.filter_by(lot_no=alnum_lotno).first()
			for i in range(0, qty):
				item = Item(lot_id=lot.id, company_id=company.id, product_id=product.id, purchase_list_id=id, delivery_id=delivery.id)
				db.session.add(item)
				purchased_item.deliveries.append(delivery)
				db.session.commit()
			return redirect(url_for('accept_delivery', company_name=company.company_name, purchase_order_no=purchase_order_no, delivery_order_no=delivery_order_no))
	return render_template('inventory_management/receive_delivery_item.html', title='Receive Item', user=user, company=company, purchase=purchase, is_my_affiliate=is_my_affiliate, is_super_admin=is_super_admin, purchased_item=purchased_item, form=form, delivery=delivery)	

	
@app.route('/<company_name>/inventory_management/deliveries', methods=['GET', 'POST'])
@login_required
def deliveries(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	purchases = Purchase.query.filter_by(company_id=company.id).order_by(Purchase.date_purchased.desc()).all()
	for purchase in purchases:
		purchase.delivered_purchases = Delivery.query.filter_by(purchase_id=purchase.id, company_id=company.id).all()
		purchase.purchase_list = PurchaseList.query.filter_by(purchase_id=purchase.id, company_id=company.id).all()
		purchase.purchase_order_complete = False
		completed_item = 0
		for list in purchase.purchase_list:
			list.delivered_qty = Item.query.filter_by(purchase_list_id=list.id, company_id=company.id).count()
			list.complete_item_delivery = list.delivered_qty == list.quantity
		for n in range(0, len(purchase.purchase_list)):
			if list.complete_item_delivery:
				completed_item += 1
		if len(purchase.purchase_list) == completed_item:
			purchase.purchase_order_complete = True
		#print(completed_item , len(purchase.purchase_list))
	is_super_admin = company.is_super_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	is_inv_admin = company.is_inv_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	form = AcceptDeliveryForm()
	if form.validate_on_submit():
		purchase = Purchase.query.filter_by(purchase_order_no=form.purchase_no.data, company_id=company.id).first_or_404()
		delivery = Delivery(delivery_no=form.delivery_no.data, receiver_id=user.id, company_id=company.id, purchase_id=purchase.id)
		db.session.add(delivery)
		db.session.commit()
		return redirect(url_for('accept_delivery', company_name=company.company_name, purchase_order_no=purchase.purchase_order_no, delivery_order_no=delivery.delivery_no))
	return render_template('inventory_management/deliveries.html', title='Deliveries', user=user, company=company, is_super_admin=is_super_admin, is_inv_supervisor=is_inv_supervisor, is_inv_admin=is_inv_admin, is_my_affiliate=is_my_affiliate, purchases=purchases, form=form)
	
@app.route('/<company_name>/inventory_management/suppliers',  methods=['GET', 'POST'])
@login_required
def suppliers(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	form = SupplierRegistrationForm()
	if form.validate_on_submit():
		supp = Supplier.query.filter_by(name=form.supplier_name.data).first()
		if supp is not None:
			company.suppliers.append(supp)
		else:
			supplier = Supplier(name=form.supplier_name.data, address=form.address.data, email=form.email.data, contact=form.contact.data, user_id=current_user.id)
			db.session.add(supplier)
			company.suppliers.append(supplier)
		db.session.commit()
		return redirect(url_for('suppliers', company_name=company.company_name))
	suppliers = Supplier.query.order_by(Supplier.name.asc()).all()
	return render_template('inventory_management/suppliers.html', title='Suppliers', user=user, form=form, suppliers=suppliers, company=company, is_super_admin=is_super_admin, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor)


'''@app.route('/edit_supplier/<int:supp_id>, <int:comp_id>', methods=['GET', 'POST'])
def edit_supplier(supp_id, comp_id):
	company = Company.query.filter_by(id=comp_id).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	supplier = Supplier.query.filter_by(id=supp_id)
	is_super_admin = company.is_super_admin(user)
	form = SupplierRegistrationForm()
	if form.submit.data:
		if form.validate_on_submit():
			dept.name = form1.dept_name.data
			db.session.commit()
			return redirect(url_for('departments', company_name=company.company_name))	
	elif request.method == 'GET':
		form1.dept_name.data = dept.name
	departments = Department.query.order_by(Department.name.asc()).all()
	return render_template('inventory_management/departments.html', title='Departments', form1=form1, departments=departments, is_super_admin=is_super_admin, company=company)'''


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
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
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
			department_name = Department(name=form1.dept_name.data, abbrv = form1.dept_abbrv.data, user_id=current_user.id)
			db.session.add(department_name)
			company.departments.append(department_name)
		db.session.commit()
		return redirect(url_for('departments', company_name=company.company_name))	
	if form2.validate_on_submit():
		type = Type.query.filter_by(name=form2.type_name.data).first()
		if type is not None:
			company.types.append(type)
		else:
			type_name = Type(name=form2.type_name.data, user_id=current_user.id)
			db.session.add(type_name)
			company.types.append(type_name)
		db.session.commit()
		return redirect(url_for('departments', company_name=company.company_name))	
	departments = Department.query.order_by(Department.name.asc()).all()
	types = Type.query.order_by(Type.name.asc()).all()
	return render_template('inventory_management/departments.html', title='Departments', user=user, form1=form1, form2=form2, types=types, company=company, is_super_admin=is_super_admin, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor, departments=departments)

@app.route('/remove_dept/<int:dept_id>, <int:comp_id>')
@login_required
def remove_dept(dept_id, comp_id):
	company = Company.query.get(comp_id)
	dept = Department.query.get(dept_id)
	dept.remove_company(company)
	db.session.commit()
	flash('Department name removed.')
	return redirect(url_for('departments', company_name=company.company_name))
	
@app.route('/edit_dept/<int:id>, <int:comp_id>', methods=['GET', 'POST'])
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
	return render_template('inventory_management/departments.html', title='Departments', form1=form1, departments=departments, is_super_admin=is_super_admin, company=company)

@app.route('/remove_type/<int:type_id>, <int:comp_id>', methods=['GET', 'POST'])
@login_required
def remove_type(type_id, comp_id):
	company = Company.query.get(comp_id)
	type = Type.query.get(type_id)
	type.remove_company(company)
	db.session.commit()
	flash('Type name deleted.')
	return redirect(url_for('departments', company_name=company.company_name))
	
@app.route('/edit_type/<int:id>, <int:comp_id>', methods=['GET', 'POST'])
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
	return render_template('inventory_management/departments.html', title='Departments', form1=form1, types=types, is_super_admin=is_super_admin, company=company)
	

@app.route('/<company_name>/document_control/', methods=['GET', 'POST'])
@login_required
def document_control(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	departments = DocumentationDepartment.query.filter_by(company_id=company.id).all()
	for dept in departments:
		dept.documents = DocumentName.query.filter_by(company_id=company.id, department_id=dept.id).all()
	is_super_admin = company.is_super_admin(user)
	is_doc_supervisor = company.is_doc_supervisor(user)
	is_doc_admin = company.is_doc_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	form1 = DepartmentRegistrationForm()
	if form1.submit.data:
		if form1.validate_on_submit():
			dept = DocumentationDepartment(department_name=form1.department_name.data, dept_abbrv=form.dept_abbrv.data, company_id=company.id, user_id=current_user.id)
			db.session.add(dept)
			db.session.commit()
			return redirect(url_for('document_control', company_name=company.company_name))
	form2 = CreateDocumentForm()
	if form2.submit.data:
		if form2.validate_on_submit():
			dept_id = DocumentationDepartment.query.filter_by(department_name=form2.dept_name.data).first().id
			doc = DocumentName(document_no=form2.document_no.data, document_name=form2.document_name.data, company_id=company.id, user_id=current_user.id, department_id=dept_id)
			db.session.add(doc)
			db.session.commit()
			return redirect(url_for('document_control', company_name=company.company_name))
	return render_template('document_control.html', title='Document Control', user=user, company=company, is_super_admin=is_super_admin, is_doc_supervisor=is_doc_supervisor, is_doc_admin=is_doc_admin, is_my_affiliate=is_my_affiliate, form1=form1, form2=form2, departments=departments)

@app.route('/<company_name>/documents/<department_name>/<document_no>/<document_name>', methods=['GET', 'POST'])
@login_required
def documents(company_name, department_name, document_no, document_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	department = DocumentationDepartment.query.filter_by(company_id=company.id, department_name=department_name).first()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	document = DocumentName.query.filter_by(company_id=company.id, document_no=document_no, document_name=document_name).first()
	sections = DocumentSection.query.filter_by(company_id=company.id, department_id=department.id, document_name_id=document.id).order_by(DocumentSection.section_number.asc()).all()
	for sect in sections:
		for s in sect.body:
			s.body = markdown2.markdown(s.section_body)
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	form1 = CreateDocumentSectionForm()
	if form1.validate_on_submit():
		section = DocumentSection(section_number=form1.section_number.data, section_title=form1.section_title.data, company_id=company.id, department_id=department.id, document_name_id=document.id, user_id=current_user.id)
		db.session.add(section)
		db.session.commit()
		return redirect(url_for('documents', company_name=company.company_name, department_name=department.department_name, document_no=document.document_no, document_name=document.document_name))
	return render_template('lab_document.html', user=user, company=company, is_super_admin=is_super_admin, is_my_affiliate=is_my_affiliate, department=department, document=document, sections=sections, form1=form1)
	
@app.route('/<company_name>/documents/<department_name>/<document_no>/<document_name>/<section_number>/<section_title>/edit', methods=['GET', 'POST'])
@login_required
def edit_section_body(company_name, department_name, document_no, document_name, section_number, section_title):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	department = DocumentationDepartment.query.filter_by(company_id=company.id, department_name=department_name).first()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	document = DocumentName.query.filter_by(company_id=company.id, document_no=document_no, document_name=document_name).first()
	section = DocumentSection.query.filter_by(company_id=company.id, department_id=department.id, document_name_id=document.id, section_number=section_number, section_title=section_title).first()
	#for sect in section.body:
	#	sect.section_body = 
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	form2 = EditDocumentBodyForm()
	if form2.validate_on_submit():
		body = DocumentSectionBody(section_body=form2.body.data, change_log=form2.changelog.data, company_id=company.id, department_id=department.id, document_name_id=document.id, document_section_id=section.id, submitted_by=current_user.id)
		db.session.add(body)
		db.session.commit()
		return redirect(url_for('documents', company_name=company.company_name, department_name=department.department_name, document_no=document.document_no, document_name=document.document_name))
	elif request.method == 'GET':
		for sect in section.body:
			form2.body.data = sect.section_body 
	return render_template('lab_document.html', user=user, company=company, is_super_admin=is_super_admin, is_my_affiliate=is_my_affiliate, department=department, document=document, section=section, form2=form2)	
	
@app.route('/document_control_sample')
def document_control_sample():
	return render_template('document_control_sample.html', title='Document Control')
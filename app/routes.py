from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from flask_cors import CORS, cross_origin
from werkzeug.urls import url_parse
from app import app, db, photos
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm, ProductRegistrationForm, EditProductForm, DepartmentRegistrationForm, DepartmentEditForm, TypeRegistrationForm, TypeEditForm, SupplierRegistrationForm, InventorySearchForm, CompanyRegistrationForm, CompanyProfileForm, UserRoleForm, CreateOrderIDForm, OrderListForm, EditOrderListForm, CreatePurchaseOrderForm, ItemReceiveForm, AcceptDeliveryForm, ConsumeItemForm, CommentForm, MessageForm, CreateDocumentForm, MessageFormDirect, CreateDocumentSectionForm, EditDocumentSectionForm, EditDocumentBodyForm, AccountsQueryForm, DocumentSubmitForm, RegisterMachineForm, RegisterAnalyteForm, RegisterReagentLotForm, RegisterControlForm, RegisterQCLotForm, QCResultForm, InternalRequestForm, InternalRequestTransferForm, AssignSupervisorForm, StripeIDForm, QCCommentForm, EncodeQcResultForm, ExcludeResultForm
from app.models import User, Post, Product, Item, Department, Supplier, Type, Order, Company, Affiliates, MyProducts, OrdersList, Purchase, PurchaseList, Delivery, Item, Lot, Comment, CommentReply, Message, DocumentName, DocumentationDepartment, DocumentSection, DocumentSectionBody, DocumentVersion, MySupplies, MyDepartmentSupplies, Machine, Analyte, Control, ReagentLot, ControlLot, Unit, CompanyAnalyteVariables, QCResult, QCValues, InternalRequest, InternalRequestList, CancelledPurchaseListPending, QCResults
from datetime import datetime, timedelta, time, date
from dateutil import parser
from app.email import send_password_reset_email
from link_preview import link_preview
import requests
import markdown2
import stripe
import json
import statistics 

stripe.api_key = app.config['STRIPE_SECRET_KEY']

# TO DO
# - reaffiliate/rehire code
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
	superuser = User.query.filter_by(id=1).first_or_404()
	companies = Company.query.order_by(Company.company_name.desc()).all()
	users = User.query.order_by(User.username.desc()).all()
	form = PostForm()
	if form.submit_url.data:
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
	if form.submit_text.data:
		if form.post.data:
			post = Post(body=form.post.data, author=current_user)
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
	return render_template('index.html', title='Home', superuser=superuser, form=form, posts=posts.items, next_url=next_url, prev_url=prev_url, user=user, companies=companies, users=users)

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
	

@app.route('/terms_of_service')
def terms_of_service():
	return render_template('terms_of_service.html', title='LABAPP Terms of Service')
	
@app.route('/privacy_policy')
def privacy_policy():
	return render_template('privacy_policy.html', title='LABAPP Terms of Service')
	

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
	superuser = User.query.filter_by(id=1).first_or_404()
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
	return render_template('user.html', title=user.username, user=user, posts=posts.items, prev_url=prev_url, next_url=next_url, form=form, my_affiliates=my_affiliates, companies=companies, users=users, superuser=superuser)
		

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	companies = Company.query.order_by(Company.company_name.desc()).all()
	users = User.query.order_by(User.username.desc()).all()
	form = EditProfileForm(current_user.username, current_user.email)
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
	return render_template('edit_profile.html', title='Edit Profile', form=form, user=user, companies=companies, users=users, superuser=superuser)
	
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


@app.route('/<username>/followers')
@login_required
def followers(username):
	this_user = User.query.filter_by(username=username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	companies = Company.query.order_by(Company.company_name.desc()).all()
	users = User.query.order_by(User.username.desc()).all()
	for user in users:
		user.my_affiliates = Affiliates.query.filter(Affiliates.start_date.isnot(None)).filter_by(user_id=user.id).all()
	return render_template('followers.html', title='Followers', companies=companies, this_user=this_user, users=users, superuser=superuser)

@app.route('/<username>/following')
@login_required
def following(username):
	this_user = User.query.filter_by(username=username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	companies = Company.query.order_by(Company.company_name.desc()).all()
	users = User.query.order_by(User.username.desc()).all()
	for user in users:
		user.my_affiliates = Affiliates.query.filter(Affiliates.start_date.isnot(None)).filter_by(user_id=user.id).all()
	return render_template('following.html', title='Following', companies=companies, this_user=this_user, users=users, superuser=superuser)

	
@app.route('/explore')
@login_required
@cross_origin()
def explore():
	user = User.query.filter_by(username=current_user.username).first()
	superuser = User.query.filter_by(id=1).first_or_404()
	companies = Company.query.order_by(Company.company_name.desc()).all()
	users = User.query.order_by(User.username.desc()).all()
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.timestamp.desc()).paginate(
		page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('explore', page=posts.next_num) \
		if posts.has_next else None
	prev_url = url_for('explore', page=posts.prev_num) \
		if posts.has_prev else None
	return render_template('index.html', title='Explore', user=user, posts=posts.items, next_url=next_url, prev_url=prev_url, companies=companies, users=users, superuser=superuser)


@app.route('/post/<int:id>', methods=['GET', 'POST'])
@login_required
def post(id):
	user = User.query.filter_by(username=current_user.username).first()
	superuser = User.query.filter_by(id=1).first_or_404()
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
	return render_template('post.html', title='Post', user=user, post=post, upvotes=upvotes, downvotes=downvotes, upvoted=upvoted, downvoted=downvoted, form=form, comments=comments, companies=companies, users=users, superuser=superuser)
	

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
	superuser = User.query.filter_by(id=1).first_or_404()
	companies = Company.query.order_by(Company.company_name.desc()).all()
	users = User.query.order_by(User.username.desc()).all()
	affiliates = Affiliates.query.filter_by(company_id=company.id, accepted=True, end_date=None).all()
	pending_affiliates = Affiliates.query.filter_by(company_id=company.id, start_date=None).all()
	is_my_affiliate = company.is_my_affiliate(user)
	is_pending_affiliate = company.is_pending_affiliate(user)
	is_super_admin = company.is_super_admin(user)
	return render_template('company.html', company=company, user=user, affiliates=affiliates, pending_affiliates=pending_affiliates,  is_my_affiliate=is_my_affiliate, is_pending_affiliate=is_pending_affiliate, is_super_admin=is_super_admin, companies=companies, users=users, superuser=superuser)

@app.route('/register_company/', methods=['GET', 'POST'])
@login_required
def register_company():
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	companies = Company.query.order_by(Company.company_name.desc()).all()
	users = User.query.order_by(User.username.desc()).all()
	form = CompanyRegistrationForm()
	if form.validate_on_submit():
		company = Company(company_name=form.company_name.data, company_abbrv=form.company_abbrv.data, about_me=form.about_me.data, email=form.email.data,  address=form.address.data, contact_info=form.contact_info.data, user_id=current_user.id)
		company.company_created = datetime.utcnow()
		if form.logo.data:
			logo_filename = photos.save(form.logo.data)
			company.logo = photos.url(logo_filename)
		db.session.add(company)
		db.session.commit()
		accept = Affiliates(super_admin=True, start_date=datetime.utcnow())
		accept.user_id = current_user.id
		company.affiliate.append(accept)
		db.session.commit()
		flash('Your changes has been saved!')
		return redirect(url_for('company', company_name=company.company_name))
	return render_template('company_profile.html', form=form, user=user, companies=companies, users=users, superuser=superuser)


@app.route('/edit_company_profile/<company_name>', methods=['GET', 'POST'])
@login_required
def edit_company_profile(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	companies = Company.query.order_by(Company.company_name.desc()).all()
	users = User.query.order_by(User.username.desc()).all()
	affiliates = Affiliates.query.filter_by(company_id=company.id, accepted=True, end_date=None).all()
	pending_affiliates = Affiliates.query.filter_by(company_id=company.id, start_date=None).all()
	is_my_affiliate = company.is_my_affiliate(user)
	is_pending_affiliate = company.is_pending_affiliate(user)
	is_super_admin = company.is_super_admin(user)
	form = CompanyProfileForm(company.company_name, company.email)
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
	return render_template('company_profile.html', form=form, company=company, user=user, affiliates=affiliates, pending_affiliates=pending_affiliates,  is_my_affiliate=is_my_affiliate, is_pending_affiliate=is_pending_affiliate, is_super_admin=is_super_admin, companies=companies, users=users, superuser=superuser)

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
	superuser = User.query.filter_by(id=1).first_or_404()
	affiliate = Affiliates.query.filter(Affiliates.start_date.isnot(None)).filter_by(user_id=user_id, company_id=comp_id, end_date=None).first()
	is_super_admin = company.is_super_admin(user)
	if not is_super_admin:
		return redirect(url_for('company', company_name=company.company_name))
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	inv_subscription_qty = 0
	plan_nickname = ''
	inv_sup_count = company.inv_supervisor_count()
	if company.stripe_id:
		stripe_cust = stripe.Customer.retrieve(company.stripe_id)
		for data in stripe_cust.subscriptions.data:
			for item in data['items']:
				inv_subscription_qty = item['quantity']
				plan_nickname = item['plan']['nickname']
	inv_sup_qty_remaining = int(inv_subscription_qty)-inv_sup_count
	form = UserRoleForm()
	if form.submit.data:
		if form.validate_on_submit():
			affiliate.title = form.title.data
			affiliate.start_date = form.start_date.data
			if form.super_admin.data:
				if inv_sup_qty_remaining > 0:
					affiliate.inv_supervisor = True
					affiliate.inv_admin = True
					affiliate.super_admin = True
					db.session.commit()
					flash('Your changes has been saved!')
					return redirect(url_for('admin', company_name=company.company_name))
				else:
					flash('No more inventory supervisor role available, please purchase additional inventory supervisor roles or reassign one.')
					return redirect(url_for('manage_affiliate', user_id=affiliate.user_id, comp_id=company.id))
				'''affiliate.qc_supervisor = True
				affiliate.qc_admin = True
				
				affiliate.doc_supervisor = True
				affiliate.doc_admin = True'''
				
			if form.inv_supervisor.data:
				if inv_sup_qty_remaining > 0:
					affiliate.inv_supervisor = form.inv_supervisor.data
					affiliate.inv_admin = form.inv_admin.data
					db.session.commit()
					flash('Your changes has been saved!')
					return redirect(url_for('admin', company_name=company.company_name))
				else:
					flash('No more inventory supervisor role available, please purchase additional inventory supervisor roles or reassign one.')
					return redirect(url_for('manage_affiliate', user_id=affiliate.user_id, comp_id=company.id))
			else:
				if form.inv_admin.data:
					if inv_sup_qty_remaining > 0:
						affiliate.inv_supervisor = True
						affiliate.inv_admin = True
						db.session.commit()
						flash('Your changes has been saved!')
						return redirect(url_for('admin', company_name=company.company_name))
					else:
						flash('No more inventory supervisor role available, please purchase additional inventory supervisor roles or reassign one.')
						return redirect(url_for('manage_affiliate', user_id=affiliate.user_id, comp_id=company.id))
				else:
					affiliate.inv_supervisor = form.inv_supervisor.data
					affiliate.inv_admin = form.inv_admin.data
					affiliate.super_admin = form.super_admin.data
					db.session.commit()
					flash('Your changes has been saved!')
					return redirect(url_for('admin', company_name=company.company_name))
			'''affiliate.qc_supervisor = form.qc_supervisor.data
			affiliate.qc_admin = form.qc_admin.data
			affiliate.doc_supervisor = form.doc_supervisor.data
			affiliate.doc_admin = form.doc_admin.data
			affiliate.super_admin = form.super_admin.data'''
			
			
			'''if form.qc_admin.data:
				affiliate.qc_supervisor = True
			
			if form.doc_admin.data:
				affiliate.doc_supervisor = True'''
			
				
				
			#db.session.commit()
			#flash('Your changes has been saved!')
			return redirect(url_for('admin', company_name=company.company_name))
	elif request.method == 'GET':
		form.title.data = affiliate.title
		form.start_date.data = affiliate.start_date
		form.qc_supervisor.data = affiliate.qc_supervisor
		form.inv_supervisor.data = affiliate.inv_supervisor
		form.doc_supervisor.data = affiliate.doc_supervisor
		form.qc_admin.data = affiliate.qc_admin
		form.inv_admin.data = affiliate.inv_admin
		form.doc_admin.data = affiliate.doc_admin
		form.super_admin.data = affiliate.super_admin
	return render_template('manage_affiliate_role.html', user=user, form=form, company=company, affiliate=affiliate, is_my_affiliate=is_my_affiliate, is_super_admin=is_super_admin, superuser=superuser, inv_sup_qty_remaining=inv_sup_qty_remaining, plan_nickname=plan_nickname)

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
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	affiliates = Affiliates.query.filter(Affiliates.start_date.isnot(None)).filter_by(company_id=company.id, end_date=None).all()
	inv_sup_count = company.inv_supervisor_count()
	pending_affiliates = Affiliates.query.filter_by(company_id=company.id, start_date=None).all()
	past_affiliates = Affiliates.query.filter(Affiliates.end_date.isnot(None), Affiliates.start_date.isnot(None)).filter_by(company_id=company.id).order_by(Affiliates.start_date.desc()).all()
	inv_subscription_qty = 0
	plan_nickname = ''
	if company.stripe_id:
		stripe_cust = stripe.Customer.retrieve(company.stripe_id)
		for data in stripe_cust.subscriptions.data:
			for item in data['items']:
				inv_subscription_qty = item['quantity']
				plan_nickname = item['plan']['nickname']
				#print(item['plan']['nickname'])
				#print(item['quantity'])
			#print(data['items'])
		#print(stripe_cust)
	inv_sup_qty_remaining = int(inv_subscription_qty)-inv_sup_count
	form = StripeIDForm()
	if form.validate_on_submit():
		company.stripe_id = form.stripe_id.data
		db.session.commit()
		return redirect(url_for('admin', company_name=company.company_name))
	elif request.method == 'GET':
		form.stripe_id.data = company.stripe_id
	is_super_admin = company.is_super_admin(user)
	if not is_super_admin:
		return redirect(url_for('company', company_name=company.company_name))
	is_my_affiliate = company.is_my_affiliate(user)
	if is_my_affiliate:
		return render_template('admin.html', title='Admin', user=user, form=form, company=company, affiliates=affiliates, pending_affiliates=pending_affiliates, past_affiliates=past_affiliates, is_my_affiliate=is_my_affiliate, is_super_admin=is_super_admin, superuser=superuser, inv_subscription_qty=inv_subscription_qty, plan_nickname=plan_nickname, inv_sup_qty_remaining=inv_sup_qty_remaining)
	else:
		return redirect(url_for('company', company_name=company.company_name))


#-------------------------------------------------------------------------------------------------
@app.route('/public-key', methods=['GET'])
def get_public_key():
    return jsonify(publicKey=app.config['STRIPE_PUBLISHABLE_KEY'])
	
@app.route('/create-customer', methods=['POST'])
def create_customer():
    # Reads application/json and returns a response
    data = json.loads(request.data)
    paymentMethod = data['payment_method']
    print(paymentMethod)
    try:
        # This creates a new Customer and attaches the PaymentMethod in one API call.
        customer = stripe.Customer.create(
            payment_method=paymentMethod,
            email=data['email'],
            invoice_settings={
                'default_payment_method': paymentMethod
            }
        )
        # At this point, associate the ID of the Customer object with your
        # own internal representation of a customer, if you have one.
        print(customer)

        # Subscribe the user to the subscription created
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[
                {
                    "plan": os.getenv("SUBSCRIPTION_PLAN_ID"),
                },
            ],
            expand=["latest_invoice.payment_intent"]
        )
        return jsonify(subscription)
    except Exception as e:
        return jsonify(e), 403


@app.route('/subscription', methods=['POST'])
def getSubscription():
    # Reads application/json and returns a response
    data = json.loads(request.data)
    try:
        subscription = stripe.Subscription.retrieve(data['subscriptionId'])
        return jsonify(subscription)
    except Exception as e:
        return jsonify(e), 403
		

#-----------------------------------------------------------------------------------------

#stripe checkeout server side
@app.route('/setup', methods=['GET'])
@login_required
def get_publishable_key():
    return jsonify({'publicKey': app.config['STRIPE_PUBLISHABLE_KEY'], 'invPlan': app.config['INV_SUP_SUBSCRIPTION_PLAN_ID']})
	#return jsonify({'publicKey': os.getenv('STRIPE_PUBLISHABLE_KEY'), 'basicPlan': os.getenv('BASIC_PLAN_ID'), 'proPlan': os.getenv('PRO_PLAN_ID')})

# Fetch the Checkout Session to display the JSON result on the success page
@app.route('/checkout-session', methods=['GET'])
@login_required
def get_checkout_session():
    id = request.args.get('sessionId')
    checkout_session = stripe.checkout.Session.retrieve(id)
    return jsonify(checkout_session)
	
@app.route('/create-checkout-session', methods=['GET','POST'])
def create_checkout_session():
    #data = json.loads(request.data)
    domain_url = app.config['DOMAIN']

    try:
        # Create new Checkout Session for the order
        # Other optional params include:
        # [billing_address_collection] - to display billing address details on the page
        # [customer] - if you have an existing Stripe Customer ID
        # [customer_email] - lets you prefill the email input in the form
        # For full details see https:#stripe.com/docs/api/checkout/sessions/create

        # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url +
            "/success.html?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url + "/canceled.html",
            payment_method_types=["card"],
			subscription_data={"items": [{"plan": app.config['INV_SUP_SUBSCRIPTION_PLAN_ID']}]}
            #subscription_data={"items": [{"plan": data['planId']}]}
        )
        return jsonify({'sessionId': checkout_session['id']})
    except Exception as e:
        return jsonify(e), 40

@app.route('/admin/<company_name>/checkout')
def checkout(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	is_super_admin = company.is_super_admin(user)
	if not is_super_admin:
		return redirect(url_for('company', company_name=company.company_name))
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	return render_template('checkout.html', title='Checkout', superuser=superuser, is_my_affiliate=is_my_affiliate, company=company, is_super_admin=is_super_admin)
		

@app.route('/admin/<company_name>/success')
def success(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	is_super_admin = company.is_super_admin(user)
	if not is_super_admin:
		return redirect(url_for('company', company_name=company.company_name))
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	return render_template('success.html', title='Success', superuser=superuser)

#----------------------------------------------------------------------------------------------------------------		


@app.route('/guides')
def guides():
	superuser = User.query.filter_by(id=1).first_or_404()
	return render_template('guides.html', title='Guides', superuser=superuser)	

				
@app.route('/calculators')
def calculators():
	superuser = User.query.filter_by(id=1).first_or_404()
	return render_template('calculators.html', title='Calculators', superuser=superuser)
	
@app.route('/quality_control_')
def quality_control_sample():
	superuser = User.query.filter_by(id=1).first_or_404()
	return render_template('quality_control_basic.html', title='Quality Control', superuser=superuser)
		

@app.route('/<company_name>/quality_control', methods=['GET', 'POST'])
@login_required
def quality_control(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	affiliate = Affiliates.query.filter_by(user_id=user.id, company_id=company.id, accepted=True).first()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	return render_template('quality_control/quality_control_company.html', title='Quality Control', user=user, company=company, is_super_admin=is_super_admin, superuser=superuser)
	
	
@app.route ('/update_analyte_list', methods=['GET', 'POST'])
@login_required
def update_analyte_list():
	machine = request.args.get('machine_id')
	company = request.args.get('company_id')
	analyte = ""
	if machine == "0":
		analytes = CompanyAnalyteVariables.query.filter_by(company_id=company).all()
	else:
		analytes = CompanyAnalyteVariables.query.filter_by(company_id=company, machine_id=machine).all()
	analyte_list = [(0, '')] + [(a.analyte.id, a.analyte.analyte) for a in analytes]
	return jsonify(result = analyte_list)
	
@app.route ('/update_rlot_list', methods=['GET', 'POST'])
@login_required
def update_rlot_list():
	company_id = request.args.get('company_id')
	analyte_id = request.args.get('analyte_id')
	company = Company.query.filter_by(id=company_id).first()
	rlot = company.reagent_lot.all()
	analyte = ""
	rlot_list = ""
	if analyte_id != "0":
		analyte = company.analyte.filter_by(id=analyte_id).first()
		analyte_rlot = analyte.reagent_lot.all()
		new_list = set(rlot) & set(analyte_rlot)
		rlot_list = [(0, '')] + [(a.id, a.lot_no) for a in new_list]
	else:
		analyte = rlot
		rlot_list = [(0, '')] + [(a.id, a.lot_no) for a in analyte]
	return jsonify(result = rlot_list)
	
	
@app.route ('/update_control_list', methods=['GET', 'POST'])
@login_required
def update_control_list():
	company_id = request.args.get('company_id')
	machine_id = request.args.get('machine_id')
	analyte_id = request.args.get('analyte_id')
	company = Company.query.filter_by(id=company_id).first()
	controls = ""
	controls_list = ""
	if machine_id == "0" and analyte_id == "0":
		#controls = QCValues.query.filter_by(company_id=company_id).all()
		#controls = company.control_lot.order_by(ControlLot.expiry.desc())
		controls = company.qc_values.join(ControlLot).order_by(ControlLot.expiry.desc()).all()
		controls_list = [(0, '')] + [(c.control_lot, "(" + n.control_name + " - " + str(c.qc_lot.lot_no) + " - " + str(c.qc_lot.expiry) + ") - (" + str(c.analyte.analyte) + ") ") for c in controls for n in c.qc_lot.control]
		#controls_list = [(0, '')] + [(c.id, n.control_name + " - " + str(c.lot_no) + " - " + str(c.expiry)) for c in controls for n in c.control]
	elif analyte_id == "0" and machine_id != "0":
		#controls = QCValues.query.filter_by(machine_id=machine_id, company_id=company_id).all()
		#controls = company.control_lot.filter(QCValues.machine_id==3).order_by(ControlLot.expiry.desc())
		controls = company.qc_values.filter_by(machine_id=machine_id).join(ControlLot).order_by(ControlLot.expiry.desc()).all()
		controls_list = [(0, '')] + [(c.control_lot, "(" + n.control_name + " - " + str(c.qc_lot.lot_no) + " - " + str(c.qc_lot.expiry) + ") - (" + str(c.analyte.analyte) + ") ") for c in controls for n in c.qc_lot.control]
		#controls_list = [(0, '')] + [(c.id, n.control_name + " - " + str(c.lot_no) + " - " + str(c.expiry)) for c in controls for n in c.control]
	else:
		#controls = QCValues.query.filter_by(analyte_id=analyte_id, machine_id=machine_id, company_id=company_id).all()
		controls = company.qc_values.filter_by(analyte_id=analyte_id, machine_id=machine_id).join(ControlLot).order_by(ControlLot.expiry.desc()).all()
		for c in controls:
			if c.reagent_lot_id:
				controls_list = [(0, '')] + [(c.control_lot, "(" + n.control_name + " - " + str(c.qc_lot.lot_no) + " - " + str(c.qc_lot.expiry) + ") - (" + str(c.analyte.analyte) + " - " + str(c.reagent_lot.lot_no) + ")") for c in controls for n in c.qc_lot.control]
			else:
				controls_list = [(0, '')] + [(c.control_lot, "(" + n.control_name + " - " + str(c.qc_lot.lot_no) + " - " + str(c.qc_lot.expiry) + ") - (" + str(c.analyte.analyte) + ")") for c in controls for n in c.qc_lot.control]
	return jsonify(result = controls_list)

@app.route('/<company_name>/quality_control/variables', methods=['GET', 'POST'])
@login_required
def qc_variables(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	affiliate = Affiliates.query.filter_by(user_id=user.id, company_id=company.id, accepted=True).first()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	control_lots = ControlLot.query.all()
	reagent_lots = ReagentLot.query.all()
	machines = Machine.query.all()
	analytes = Analyte.query.all()
	units = Unit.query.all()
	#dept = company.documentation_department
	#dept_list = [(d.id, d.department_name) for d in dept]
	comp_analyte = company.analyte.order_by(Analyte.analyte.asc())
	analyte_list = [(0, '')] + [(a.id, a.analyte) for a in comp_analyte]
	comp_controls = company.control.order_by(Control.control_name.asc())
	control_list = [(0, '')] + [(c.id, c.control_name) for c in comp_controls]
	form1 = RegisterMachineForm()
	if form1.validate_on_submit():
		machine_query = Machine.query.filter_by(machine_name=form1.rmf_machine_name.data).first()
		if machine_query is None:
			machine = Machine(machine_name=form1.rmf_machine_name.data)
			db.session.add(machine)
			company.machine.append(machine)
			db.session.commit()
			return redirect(url_for('qc_variables', company_name=company.company_name))
		else:
			company.machine.append(machine_query)
			db.session.commit()
			return redirect(url_for('qc_variables', company_name=company.company_name))
	machine = company.machine.order_by(Machine.machine_name.asc())
	machine_list = [(0, '')] + [(m.id, m.machine_name) for m in machine]
	form2 = RegisterAnalyteForm()
	form2.raf_machine.choices = machine_list
	if form2.validate_on_submit():
		analyte_query = Analyte.query.filter_by(analyte=form2.raf_analyte.data).first()
		unit_query = Unit.query.filter_by(unit=form2.raf_unit.data).first()
		if analyte_query is None:
			analyte = Analyte(analyte=form2.raf_analyte.data)
			db.session.add(analyte)
			company.analyte.append(analyte)
			db.session.commit()
			if unit_query is None:
				unit = Unit(unit=form2.raf_unit.data)
				db.session.add(unit)
				db.session.commit()
				analyte_unit = CompanyAnalyteVariables(unit_id=unit.id, company_id=company.id, analyte_id=analyte.id, machine_id=form2.raf_machine.data)
				db.session.add(analyte_unit)
				db.session.commit()
			else:
				analyte_unit = CompanyAnalyteVariables(unit_id=unit_query.id, company_id=company.id, analyte_id=analyte.id, machine_id=form2.raf_machine.data)
				db.session.add(analyte_unit)
				db.session.commit()
		else:
			company.analyte.append(analyte_query)
			db.session.commit()
			if unit_query is None:
				unit = Unit(unit=form2.raf_unit.data)
				db.session.add(unit)
				db.session.commit()
				analyte_unit = CompanyAnalyteVariables(unit_id=unit.id, company_id=company.id, analyte_id=analyte_query.id, machine_id=form2.raf_machine.data)
				db.session.add(analyte_unit)
				db.session.commit()
			else:
				analyte_unit = CompanyAnalyteVariables(unit_id=unit_query.id, company_id=company.id, analyte_id=analyte_query.id, machine_id=form2.raf_machine.data)
				db.session.add(analyte_unit)
				db.session.commit()
		return redirect(url_for('qc_variables', company_name=company.company_name))
	form3 = RegisterControlForm()
	if form3.validate_on_submit():
		control_query = Control.query.filter_by(control_name=form3.rcf_control_name.data).first()
		if control_query is None:
			control = Control(control_name=form3.rcf_control_name.data)
			db.session.add(control)
			company.control.append(control)
			db.session.commit()
		else:
			company.control.append(control_query)
			db.session.commit()
		return redirect(url_for('qc_variables', company_name=company.company_name))
	form4 = RegisterReagentLotForm()
	form4.rrlf_machine.choices = machine_list
	form4.rrlf_analyte.choices = analyte_list
	if form4.validate_on_submit():
		raw_lotno = form4.rrlf_reagent_lot_no.data
		alnum_lotno = ''.join(e for e in raw_lotno if e.isalnum())
		rlot_query = ReagentLot.query.filter_by(lot_no=alnum_lotno).first()
		analyte = Analyte.query.filter_by(id=form4.rrlf_analyte.data).first()
		if rlot_query is None:
			lot_no = ReagentLot(lot_no=alnum_lotno, expiry=form4.rrlf_reagent_expiry.data)
			db.session.add(lot_no)
			company.reagent_lot.append(lot_no)
			analyte.reagent_lot.append(lot_no)
			db.session.commit()
		else:
			company.reagent_lot.append(rlot_query)
			analyte.reagent_lot.append(rlot_query)
			db.session.commit()
		return redirect(url_for('qc_variables', company_name=company.company_name))
	form5 = RegisterQCLotForm()
	form5.rqclf_control.choices = control_list
	if form5.validate_on_submit():
		raw_control_lot = form5.rqclf_control_lot_no.data
		alnum_control_lot = ''.join(e for e in raw_control_lot if e.isalnum())
		clot_query = ControlLot.query.filter_by(lot_no=alnum_control_lot).first()
		control = Control.query.filter_by(id=form5.rqclf_control.data).first()
		if clot_query is None:
			control_lot = ControlLot(lot_no=alnum_control_lot, expiry=form5.rqclf_control_expiry.data)
			db.session.add(control_lot)
			company.control_lot.append(control_lot)
			control.lot.append(control_lot)
			db.session.commit()
		else:
			company.control_lot.append(clot_query)
			control.lot.append(clot_query)
			db.session.commit()
		return redirect(url_for('qc_variables', company_name=company.company_name))
	form6 = QCResultForm()
	rgt_lot = company.reagent_lot.order_by(ReagentLot.expiry.desc())
	rgt_lot_list = [(0, '')] + [(c.id, c.lot_no) for c in rgt_lot]
	control_lot = company.control_lot.order_by(ControlLot.expiry.desc())
	'''for c in control_lot:
		c.cname = ""
		for n in c.control:
			c.cname = n.control_name
		c.lot_info = c.cname + " - " + str(c.lot_no) + " - " + str(c.expiry)'''
	#ctrl_lot_list = [(0, '')] + [(c.id, c.cname + str(c.lot_no) + " - " + str(c.expiry)) for c in control_lot]
	ctrl_lot_list = [(0, '')] + [(c.id, n.control_name + " - " + str(c.lot_no) + " - " + str(c.expiry)) for c in control_lot for n in c.control]
	form6.qcrf_analyte.choices = analyte_list
	form6.qcrf_reagent_lot.choices = rgt_lot_list
	form6.qcrf_machine.choices = machine_list
	form6.control1.choices = ctrl_lot_list
	form6.control2.choices = ctrl_lot_list
	form6.control3.choices = ctrl_lot_list
	level1_data = False
	level2_data = False
	level3_data = False
	#Control 1 2 3 are not control levels and should not be treated as such, only the number of controls that you want to encode. Do not set it as contol levels
	if form6.qcrf_submit.data:
		analyte_unit = CompanyAnalyteVariables.query.filter_by(analyte_id=form6.qcrf_analyte.data, company_id=company.id).first()
		if form6.control3.data:
			level3_data = True
			if form6.qcrf_reagent_lot.data:
				#values = QCValues(control_lot=form6.control1.data, lvl1_mean=form6.control1_mean.data, lvl1_sd=form6.control1_sd.data, lvl2_lot=form6.control2.data, lvl2_mean=form6.control2_mean.data, lvl2_sd=form6.control2_sd.data, lvl3_lot=form6.control3.data, lvl3_mean=form6.control3_mean.data, lvl3_sd=form6.control3_sd.data, machine_id=form6.qcrf_machine.data, analyte_id=form6.qcrf_analyte.data, reagent_lot_id=form6.qcrf_reagent_lot.data, company_id=company.id, unit_id=analyte_unit.unit.id)
				values1 = QCValues(control_lot=form6.control1.data, control_mean=form6.control1_mean.data, control_sd=form6.control1_sd.data, machine_id=form6.qcrf_machine.data, analyte_id=form6.qcrf_analyte.data, reagent_lot_id=form6.qcrf_reagent_lot.data, company_id=company.id, unit_id=analyte_unit.unit.id)
				values2 = QCValues(control_lot=form6.control2.data, control_mean=form6.control2_mean.data, control_sd=form6.control2_sd.data, machine_id=form6.qcrf_machine.data, analyte_id=form6.qcrf_analyte.data, reagent_lot_id=form6.qcrf_reagent_lot.data, company_id=company.id, unit_id=analyte_unit.unit.id)
				values3 = QCValues(control_lot=form6.control3.data, control_mean=form6.control3_mean.data, control_sd=form6.control3_sd.data, machine_id=form6.qcrf_machine.data, analyte_id=form6.qcrf_analyte.data, reagent_lot_id=form6.qcrf_reagent_lot.data, company_id=company.id, unit_id=analyte_unit.unit.id)
			else:
				#values = QCValues(control_lot=form6.control1.data, lvl1_mean=form6.control1_mean.data, lvl1_sd=form6.control1_sd.data, lvl2_lot=form6.control2.data, lvl2_mean=form6.control2_mean.data, lvl2_sd=form6.control2_sd.data, lvl3_lot=form6.control3.data, lvl3_mean=form6.control3_mean.data, lvl3_sd=form6.control3_sd.data, machine_id=form6.qcrf_machine.data, analyte_id=form6.qcrf_analyte.data, company_id=company.id, unit_id=analyte_unit.unit.id)
				values1 = QCValues(control_lot=form6.control1.data, control_mean=form6.control1_mean.data, control_sd=form6.control1_sd.data, machine_id=form6.qcrf_machine.data, analyte_id=form6.qcrf_analyte.data, company_id=company.id, unit_id=analyte_unit.unit.id)
				values2 = QCValues(control_lot=form6.control2.data, control_mean=form6.control2_mean.data, control_sd=form6.control2_sd.data, machine_id=form6.qcrf_machine.data, analyte_id=form6.qcrf_analyte.data, company_id=company.id, unit_id=analyte_unit.unit.id)
				values3 = QCValues(control_lot=form6.control3.data, control_mean=form6.control3_mean.data, control_sd=form6.control3_sd.data, machine_id=form6.qcrf_machine.data, analyte_id=form6.qcrf_analyte.data, company_id=company.id, unit_id=analyte_unit.unit.id)
			db.session.add(values1)
			db.session.add(values2)
			db.session.add(values3)
			db.session.commit()
			return redirect(url_for('qc_variables', company_name=company.company_name))
		elif form6.control2.data:
			level2_data = True
			if form6.qcrf_reagent_lot.data:
				#values = QCValues(control_lot=form6.control1.data, lvl1_mean=form6.control1_mean.data, lvl1_sd=form6.control1_sd.data, lvl2_lot=form6.control2.data, lvl2_mean=form6.control2_mean.data, lvl2_sd=form6.control2_sd.data, machine_id=form6.qcrf_machine.data, analyte_id=form6.qcrf_analyte.data, reagent_lot_id=form6.qcrf_reagent_lot.data, company_id=company.id, unit_id=analyte_unit.unit.id)
				values1 = QCValues(control_lot=form6.control1.data, control_mean=form6.control1_mean.data, control_sd=form6.control1_sd.data, machine_id=form6.qcrf_machine.data, analyte_id=form6.qcrf_analyte.data, reagent_lot_id=form6.qcrf_reagent_lot.data, company_id=company.id, unit_id=analyte_unit.unit.id)
				values2 = QCValues(control_lot=form6.control2.data, control_mean=form6.control2_mean.data, control_sd=form6.control2_sd.data, machine_id=form6.qcrf_machine.data, analyte_id=form6.qcrf_analyte.data, reagent_lot_id=form6.qcrf_reagent_lot.data, company_id=company.id, unit_id=analyte_unit.unit.id)
			else:
				#values = QCValues(control_lot=form6.control1.data, lvl1_mean=form6.control1_mean.data, lvl1_sd=form6.control1_sd.data, lvl2_lot=form6.control2.data, lvl2_mean=form6.control2_mean.data, lvl2_sd=form6.control2_sd.data, machine_id=form6.qcrf_machine.data, analyte_id=form6.qcrf_analyte.data, company_id=company.id, unit_id=analyte_unit.unit.id)
				values1 = QCValues(control_lot=form6.control1.data, control_mean=form6.control1_mean.data, control_sd=form6.control1_sd.data, machine_id=form6.qcrf_machine.data, analyte_id=form6.qcrf_analyte.data, company_id=company.id, unit_id=analyte_unit.unit.id)
				values2 = QCValues(control_lot=form6.control2.data, control_mean=form6.control2_mean.data, control_sd=form6.control2_sd.data, machine_id=form6.qcrf_machine.data, analyte_id=form6.qcrf_analyte.data, company_id=company.id, unit_id=analyte_unit.unit.id)
			db.session.add(values1)
			db.session.add(values2)
			db.session.commit()
			return redirect(url_for('qc_variables', company_name=company.company_name))
		elif form6.control1.data:
			level1_data = True
			if form6.qcrf_reagent_lot.data:
				values = QCValues(control_lot=form6.control1.data, control_mean=form6.control1_mean.data, control_sd=form6.control1_sd.data, machine_id=form6.qcrf_machine.data, analyte_id=form6.qcrf_analyte.data, reagent_lot_id=form6.qcrf_reagent_lot.data, company_id=company.id, unit_id=analyte_unit.unit.id)
			else:
				values = QCValues(control_lot=form6.control1.data, control_mean=form6.control1_mean.data, control_sd=form6.control1_sd.data,  machine_id=form6.qcrf_machine.data, analyte_id=form6.qcrf_analyte.data, company_id=company.id, unit_id=analyte_unit.unit.id)
			db.session.add(values)
			db.session.commit()
			return redirect(url_for('qc_variables', company_name=company.company_name))
	company_analyte_variable = CompanyAnalyteVariables.query.filter_by(company_id=company.id).all()
	return render_template('quality_control/qc_variables.html', title='Variables', user=user, company=company, is_super_admin=is_super_admin, superuser=superuser, form1=form1, form2=form2, form3=form3, form4=form4, form5=form5, form6=form6, control_lots=control_lots, reagent_lots=reagent_lots, machines=machines, analytes=analytes, units=units, company_analyte_variable=company_analyte_variable)


@app.route('/<company_name>/quality_control/upload_qc_values', methods=['GET', 'POST'])
@login_required
def encode_qc_results(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	affiliate = Affiliates.query.filter_by(user_id=user.id, company_id=company.id, accepted=True).first()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	machine = company.machine.order_by(Machine.machine_name.asc())
	machine_list = [(0, '')] + [(m.id, m.machine_name) for m in machine]
	comp_analyte = company.analyte.order_by(Analyte.analyte.asc())
	analyte_list = [(0, '')] + [(a.id, a.analyte) for a in comp_analyte]
	#comp_controls = company.control.order_by(Control.control_name.asc())
	#control_list = [(c.id, c.control_name) for c in comp_controls]
	rgt_lot = company.reagent_lot.order_by(ReagentLot.expiry.desc())
	rgt_lot_list = [(0, '')] + [(c.id, c.lot_no) for c in rgt_lot]
	#control_lot = company.control_lot.order_by(ControlLot.expiry.desc())
	#control_lot = QCValues.query.filter_by(company_id=company.id).all()
	control_lot = company.qc_values.join(ControlLot).order_by(ControlLot.expiry.desc()).all()
	#ctrl_lot_list = [(0, '')] + [(c.id, n.control_name + " - " + str(c.lot_no) + " - " + str(c.expiry)) for c in control_lot for n in c.control]#having attribute error no c.lot_info
	ctrl_lot_list = [(0, '')] + [(c.control_lot, "(" + n.control_name + " - " + str(c.qc_lot.lot_no) + " - " + str(c.qc_lot.expiry) + ") - (" + str(c.analyte.analyte) + ")") for c in control_lot for n in c.qc_lot.control]
	form = EncodeQcResultForm() #QCResultForm()
	form.eqcrf_analyte.choices = analyte_list
	form.eqcrf_reagent_lot.choices = rgt_lot_list
	form.eqcrf_machine.choices = machine_list
	form.eqcrf_control.choices = ctrl_lot_list
	#form.control2.choices = ctrl_lot_list
	#form.control3.choices = ctrl_lot_list
	if form.eqcrf_submit.data:
		#analyte = Analyte.query.filter_by(id=form.analyte.data).first()
		analyte_unit = CompanyAnalyteVariables.query.filter_by(analyte_id=form.eqcrf_analyte.data, company_id=company.id).first()
		date_list = request.form.getlist('cDate')
		level1_list = request.form.getlist('qc_data_lvl1')
		for i in range(0, len(date_list)):
			date_list[i] = parser.parse(date_list[i])
			if form.eqcrf_reagent_lot.data == 0:
				qc_results = QCResults(run_date=date_list[i], qc_result=level1_list[i], qc_lot=form.eqcrf_control.data, machine_id=form.eqcrf_machine.data, analyte_id=form.eqcrf_analyte.data, company_id=company.id, unit_id=analyte_unit.unit.id)
			else:
				qc_results = QCResults(run_date=date_list[i], qc_result=level1_list[i], qc_lot=form.eqcrf_control.data, machine_id=form.eqcrf_machine.data, analyte_id=form.eqcrf_analyte.data, reagent_lot_id=form.eqcrf_reagent_lot.data, company_id=company.id, unit_id=analyte_unit.unit.id)
			db.session.add(qc_results)
			db.session.commit()
		return redirect(url_for('encode_qc_results', company_name=company_name))
		'''if form.control3.data:
			level3_list = request.form.getlist('qc_data_lvl3')
			level2_list = request.form.getlist('qc_data_lvl2')
			level1_list = request.form.getlist('qc_data_lvl1')
			for i in range(0, len(date_list)):
				#if date_list[i] is datetime.date:
				date_list[i] = parser.parse(date_list[i])
				if form.qcrf_reagent_lot.data == 0:
					qc_results = QCResult(run_date=datetime(date_list[i].year, date_list[i].month, date_list[i].day).date(), lvl1=level1_list[i], lvl2=level2_list[i], lvl3=level3_list[i], lvl1_lot=form.control1.data, lvl2_lot=form.control2.data, lvl3_lot=form.control3.data, machine_id=form.qcrf_machine.data, analyte_id=form.qcrf_analyte.data, company_id=company.id, unit_id=analyte_unit.unit.id)
				else:
					qc_results = QCResult(run_date=datetime(date_list[i].year, date_list[i].month, date_list[i].day).date(), lvl1=level1_list[i], lvl2=level2_list[i], lvl3=level3_list[i], lvl1_lot=form.control1.data, lvl2_lot=form.control2.data, lvl3_lot=form.control3.data, machine_id=form.qcrf_machine.data, analyte_id=form.qcrf_analyte.data, reagent_lot_id=form.qcrf_reagent_lot.data, company_id=company.id, unit_id=analyte_unit.unit.id)
				db.session.add(qc_results)
				db.session.commit()
		elif form.control2.data:
			level2_list = request.form.getlist('qc_data_lvl2')
			level1_list = request.form.getlist('qc_data_lvl1')
			for i in range(0, len(date_list)):
				#if date_list[i] is datetime.date:
				date_list[i] = parser.parse(date_list[i])
				if form.qcrf_reagent_lot.data == 0:
					qc_results = QCResult(run_date=datetime(date_list[i].year, date_list[i].month, date_list[i].day).date(), lvl1=level1_list[i], lvl2=level2_list[i], lvl1_lot=form.control1.data, lvl2_lot=form.control2.data, machine_id=form.qcrf_machine.data, analyte_id=form.qcrf_analyte.data,  company_id=company.id, unit_id=analyte_unit.unit.id)
				else:
					qc_results = QCResult(run_date=datetime(date_list[i].year, date_list[i].month, date_list[i].day).date(), lvl1=level1_list[i], lvl2=level2_list[i], lvl1_lot=form.control1.data, lvl2_lot=form.control2.data, machine_id=form.qcrf_machine.data, analyte_id=form.qcrf_analyte.data, reagent_lot_id=form.qcrf_reagent_lot.data, company_id=company.id, unit_id=analyte_unit.unit.id)
				db.session.add(qc_results)
				db.session.commit()
		elif form.control1.data:
			level1_list = request.form.getlist('qc_data_lvl1')
			for i in range(0, len(date_list)):
				#if date_list[i] is datetime.date:
				#	print(date_list[i])
				#date_list[i] = parser.parse(date_list[i])
				if form.qcrf_reagent_lot.data == 0:
					#qc_results = QCResult(run_date=datetime(date_list[i].year, date_list[i].month, date_list[i].day).date(), lvl1=level1_list[i], lvl1_lot=form.control1.data, machine_id=form.qcrf_machine.data, analyte_id=form.qcrf_analyte.data, company_id=company.id, unit_id=analyte_unit.unit.id)
					qc_results = QCResults(run_date=datetime(date_list[i]), qc_result=level1_list[i], qc_lot=form.control1.data, machine_id=form.qcrf_machine.data, analyte_id=form.qcrf_analyte.data, company_id=company.id, unit_id=analyte_unit.unit.id)
				else:
					#qc_results = QCResult(run_date=datetime(date_list[i].year, date_list[i].month, date_list[i].day).date(), lvl1=level1_list[i], lvl1_lot=form.control1.data, machine_id=form.qcrf_machine.data, analyte_id=form.qcrf_analyte.data, reagent_lot_id=form.qcrf_reagent_lot.data, company_id=company.id, unit_id=analyte_unit.unit.id)
					qc_results = QCResults(run_date=datetime(date_list[i]), qc_result=level1_list[i], qc_lot=form.control1.data, machine_id=form.qcrf_machine.data, analyte_id=form.qcrf_analyte.data, reagent_lot_id=form.qcrf_reagent_lot.data, company_id=company.id, unit_id=analyte_unit.unit.id)
				db.session.add(qc_results)
				db.session.commit()
		return redirect(url_for('encode_qc_results', company_name=company_name))'''
	return render_template('quality_control/encode_qc_results.html', title='Encode Results', user=user, company=company, is_super_admin=is_super_admin, superuser=superuser, form=form, rgt_lot=rgt_lot)
	
@app.route('/<company_name>/quality_control/saved_results', methods=['GET', 'POST'])
@login_required
def saved_results(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	affiliate = Affiliates.query.filter_by(user_id=user.id, company_id=company.id, accepted=True).first()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	machine = company.machine.order_by(Machine.machine_name.asc())
	machine_list = [(0, '')] + [(m.id, m.machine_name) for m in machine]
	comp_analyte = company.analyte.order_by(Analyte.analyte.asc())
	analyte_list = [(0, '')] + [(a.id, a.analyte) for a in comp_analyte]
	rgt_lot = company.reagent_lot.order_by(ReagentLot.expiry.desc())
	rgt_lot_list = [(0, '')] + [(c.id, c.lot_no) for c in rgt_lot]
	control_lot = company.control_lot.order_by(ControlLot.expiry.desc())
	#ctrl_lot_list = [(0, '')] + [(c.id, c.lot_no) for c in control_lot]
	ctrl_lot_list = [(0, '')] + [(c.id, n.control_name + " - " + str(c.lot_no) + " - " + str(c.expiry)) for c in control_lot for n in c.control]
	form = QCResultForm()
	form.qcrf_analyte.choices = analyte_list
	form.qcrf_reagent_lot.choices = rgt_lot_list
	form.qcrf_machine.choices = machine_list
	form.control1.choices = ctrl_lot_list
	form.control2.choices = ctrl_lot_list
	form.control3.choices = ctrl_lot_list
	if form.qcrf_submit.data:
		start_date = form.start_date.data
		end_date = form.end_date.data
		qc_lot1 = form.control1.data
		qc_lot2 = form.control2.data
		qc_lot3 = form.control3.data
		machine_id=form.qcrf_machine.data
		analyte_id=form.qcrf_analyte.data
		reagent_lot_id=form.qcrf_reagent_lot.data
		return redirect(url_for('qc_results', company_name=company_name, start_date=start_date, end_date=end_date, qc_lot1=qc_lot1, qc_lot2=qc_lot2, qc_lot3=qc_lot3, machine_id=machine_id, analyte_id=analyte_id, reagent_lot_id=reagent_lot_id))
	return render_template('quality_control/qc_saved.html', title='QC Results', user=user, company=company, is_super_admin=is_super_admin, superuser=superuser, form=form, rgt_lot=rgt_lot)
	
	
@app.route('/<company_name>/quality_control/qc_results/<start_date>/<end_date>/<qc_lot1>&<qc_lot2>&<qc_lot3>&<machine_id>&<analyte_id>&<reagent_lot_id>', methods=['GET', 'POST'])
@login_required
def qc_results(company_name, start_date, end_date, qc_lot1, qc_lot2, qc_lot3, machine_id, analyte_id, reagent_lot_id):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	affiliate = Affiliates.query.filter_by(user_id=user.id, company_id=company.id, accepted=True).first()
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	machine = company.machine.filter_by(id=machine_id).first()
	analyte = company.analyte.filter_by(id=analyte_id).first()
	reagent_lot = company.reagent_lot.filter_by(id=reagent_lot_id).first()
	parsed_date = parser.parse(end_date)
	end_date_ = datetime.combine(parsed_date.date(), time(23, 59, 59))
	comments = []
	qc_values1 = ''
	qc_values2 = ''
	qc_values3 = ''
	qc_res1 = ''
	qc_res2 = ''
	qc_res3 = ''
	qc1_lot_list = []
	qc2_lot_list = []
	qc3_lot_list = []
	rgt_lot_list = []
	if reagent_lot_id == '0':		
		qc_results = QCResults.query.filter(QCResults.run_date.between(start_date, end_date_)).filter_by(machine_id=machine_id, analyte_id=analyte_id, company_id=company.id, rejected=False).order_by(QCResults.run_date.asc()).all()
		for q in qc_results:
			rgt_lot_list.append(q.reagent_lot.lot_no)
			if q.comment is not None:
				comments.append({q.run_date: q.comment})
		rgt_lot_list = set(rgt_lot_list)
		if qc_lot1 == '0':
			qc_res1 = QCResults.query.filter(QCResults.run_date.between(start_date, end_date_)).filter_by(machine_id=machine_id, analyte_id=analyte_id, company_id=company.id, rejected=False).join(ControlLot).filter_by(level = 1).order_by(QCResults.run_date.asc()).all()
			for q in qc_res1:
				qc_values1 = QCValues.query.filter_by(control_lot=q.qc_lot, machine_id=machine_id, analyte_id=analyte_id, company_id=company.id).first()
				qc1_lot_list.append(q.control_lot.lot_no)
			qc1_lot_list = (set(qc1_lot_list))
		else:
			qc_res1 = QCResults.query.filter(QCResults.run_date.between(start_date, end_date_)).filter_by(qc_lot=qc_lot1, machine_id=machine_id, analyte_id=analyte_id, company_id=company.id, rejected=False).order_by(QCResults.run_date.asc()).all()
			qc_values1 = QCValues.query.filter_by(control_lot=qc_lot1, machine_id=machine_id, analyte_id=analyte_id, company_id=company.id).first()
		if qc_lot2 == '0':
			qc_res2 = QCResults.query.filter(QCResults.run_date.between(start_date, end_date_)).filter_by(machine_id=machine_id, analyte_id=analyte_id, company_id=company.id, rejected=False).join(ControlLot).filter_by(level = 2).order_by(QCResults.run_date.asc()).all()
			for q in qc_res2:
				qc_values2 = QCValues.query.filter_by(control_lot=q.qc_lot, machine_id=machine_id, analyte_id=analyte_id, company_id=company.id).first()
				qc2_lot_list.append(q.control_lot.lot_no)
			qc2_lot_list = (set(qc2_lot_list))
		else:
			qc_res2 = QCResults.query.filter(QCResults.run_date.between(start_date, end_date_)).filter_by(qc_lot=qc_lot2, machine_id=machine_id, analyte_id=analyte_id, company_id=company.id, rejected=False).order_by(QCResults.run_date.asc()).all()
			qc_values2 = QCValues.query.filter_by(control_lot=qc_lot2, machine_id=machine_id, analyte_id=analyte_id, company_id=company.id).first()
		if qc_lot3 == '0':
			qc_res3 = QCResults.query.filter(QCResults.run_date.between(start_date, end_date_)).filter_by(machine_id=machine_id, analyte_id=analyte_id, company_id=company.id, rejected=False).join(ControlLot).filter_by(level = 3).order_by(QCResults.run_date.asc()).all()
			for q in qc_res3:
				qc_values3 = QCValues.query.filter_by(control_lot=q.qc_lot, machine_id=machine_id, analyte_id=analyte_id, company_id=company.id).first()
				qc3_lot_list.append(q.control_lot.lot_no)
			qc3_lot_list = (set(qc3_lot_list))
		else:
			qc_res3 = QCResults.query.filter(QCResults.run_date.between(start_date, end_date_)).filter_by(qc_lot=qc_lot3, machine_id=machine_id, analyte_id=analyte_id, company_id=company.id, rejected=False).order_by(QCResults.run_date.asc()).all()
			qc_values3 = QCValues.query.filter_by(control_lot=qc_lot3, machine_id=machine_id, analyte_id=analyte_id, company_id=company.id).first()
		excluded = QCResults.query.filter(QCResults.run_date.between(start_date, end_date_)).filter_by(machine_id=machine_id, analyte_id=analyte_id, company_id=company.id, rejected=True).order_by(QCResults.run_date.asc()).all()
	else:
		qc_results = QCResults.query.filter(QCResults.run_date.between(start_date, end_date_)).filter_by(machine_id=machine_id, analyte_id=analyte_id, reagent_lot_id=reagent_lot_id, company_id=company.id, rejected=False).order_by(QCResults.run_date.asc()).all()
		for q in qc_results:
			run_dates = q.run_date
			if q.comment is not None:
				comments.append({q.run_date: q.comment})
		if qc_lot1 == '0':
			qc_res1 = QCResults.query.filter(QCResults.run_date.between(start_date, end_date_)).filter_by(machine_id=machine_id, analyte_id=analyte_id, reagent_lot_id=reagent_lot_id, company_id=company.id, rejected=False).order_by(QCResults.run_date.asc()).all()
			for q in qc_res1:
				qc_values1 = QCValues.query.filter_by(control_lot=q.qc_lot, machine_id=machine_id, analyte_id=analyte_id, reagent_lot_id=reagent_lot_id, company_id=company.id).first()
				qc1_lot_list.append(q.control_lot.lot_no)
			qc1_lot_list = (set(qc1_lot_list))
		else:
			qc_res1 = QCResults.query.filter(QCResults.run_date.between(start_date, end_date_)).filter_by(qc_lot=qc_lot1, machine_id=machine_id, analyte_id=analyte_id, reagent_lot_id=reagent_lot_id, company_id=company.id, rejected=False).order_by(QCResults.run_date.asc()).all()
			qc_values1 = QCValues.query.filter_by(control_lot=qc_lot1, machine_id=machine_id, analyte_id=analyte_id, reagent_lot_id=reagent_lot_id, company_id=company.id).first()
		if qc_lot2 == '0':
			qc_res2 = QCResults.query.filter(QCResults.run_date.between(start_date, end_date_)).filter_by(machine_id=machine_id, analyte_id=analyte_id, reagent_lot_id=reagent_lot_id, company_id=company.id, rejected=False).order_by(QCResults.run_date.asc()).all()
			for q in qc_res2:
				qc_values2 = QCValues.query.filter_by(control_lot=q.qc_lot, machine_id=machine_id, analyte_id=analyte_id, reagent_lot_id=reagent_lot_id, company_id=company.id).first()
				qc2_lot_list.append(q.control_lot.lot_no)
			qc2_lot_list = (set(qc2_lot_list))
		else:
			qc_res2 = QCResults.query.filter(QCResults.run_date.between(start_date, end_date_)).filter_by(qc_lot=qc_lot2, machine_id=machine_id, analyte_id=analyte_id, reagent_lot_id=reagent_lot_id, company_id=company.id, rejected=False).order_by(QCResults.run_date.asc()).all()
			qc_values2 = QCValues.query.filter_by(control_lot=qc_lot2, machine_id=machine_id, analyte_id=analyte_id, reagent_lot_id=reagent_lot_id, company_id=company.id).first()
		if qc_lot3 == '0':
			qc_res3 = QCResults.query.filter(QCResults.run_date.between(start_date, end_date_)).filter_by(machine_id=machine_id, analyte_id=analyte_id, reagent_lot_id=reagent_lot_id, company_id=company.id, rejected=False).order_by(QCResults.run_date.asc()).all()
			for q in qc_res3:
				qc_values3 = QCValues.query.filter_by(control_lot=q.qc_lot, machine_id=machine_id, analyte_id=analyte_id, reagent_lot_id=reagent_lot_id, company_id=company.id).first()
				qc3_lot_list.append(q.control_lot.lot_no)
			qc3_lot_list = (set(qc3_lot_list))
		else:
			qc_res3 = QCResults.query.filter(QCResults.run_date.between(start_date, end_date_)).filter_by(qc_lot=qc_lot3, machine_id=machine_id, analyte_id=analyte_id, reagent_lot_id=reagent_lot_id, company_id=company.id, rejected=False).order_by(QCResults.run_date.asc()).all()
			qc_values3 = QCValues.query.filter_by(control_lot=qc_lot3, machine_id=machine_id, analyte_id=analyte_id, reagent_lot_id=reagent_lot_id, company_id=company.id).first()
		excluded = qc_results = QCResults.query.filter(QCResults.run_date.between(start_date, end_date_)).filter_by(machine_id=machine_id, analyte_id=analyte_id, reagent_lot_id=reagent_lot_id, company_id=company.id, rejected=True).order_by(QCResults.run_date.asc()).all()
	comment_form = QCCommentForm()
	if comment_form.validate_on_submit():
		qc_res_query = QCResults.query.filter_by(run_date=comment_form.qccf_result_date.data, analyte_id=analyte_id, machine_id=machine_id, company_id=company.id).first()
		if qc_res_query:
			qc_res_query.comment = comment_form.qccf_comment.data
			db.session.commit()
		return redirect(url_for('qc_results', company_name=company_name, start_date=start_date, end_date=end_date, qc_lot1=qc_lot1, qc_lot2=qc_lot2, qc_lot3=qc_lot3, machine_id=machine_id, analyte_id=analyte_id, reagent_lot_id=reagent_lot_id))
	exclude_form = ExcludeResultForm()
	if exclude_form.validate_on_submit():
		qc_res_query = QCResults.query.filter_by(run_date=exclude_form.erf_result_date.data, qc_result=exclude_form.erf_result.data, analyte_id=analyte_id, machine_id=machine_id, company_id=company.id).first()
		qc_res_query.rejected = True
		qc_res_query.comment = exclude_form.erf_comment.data
		db.session.commit()
		return redirect(url_for('qc_results', company_name=company_name, start_date=start_date, end_date=end_date, qc_lot1=qc_lot1, qc_lot2=qc_lot2, qc_lot3=qc_lot3, machine_id=machine_id, analyte_id=analyte_id, reagent_lot_id=reagent_lot_id))
	return render_template('quality_control/qc_results.html', user=user, superuser=superuser, is_super_admin=is_super_admin, company=company, machine=machine, analyte=analyte, reagent_lot=reagent_lot, qc_res1=qc_res1, qc_res2=qc_res2, qc_res3=qc_res3, qc_values1=qc_values1, qc_values2=qc_values2, qc_values3=qc_values3, comment_form=comment_form, rgt_lot_list=rgt_lot_list, qc1_lot_list=qc1_lot_list, qc2_lot_list=qc2_lot_list, qc3_lot_list=qc3_lot_list, qc_results=qc_results, comments=comments, exclude_form=exclude_form, excluded=excluded)

@app.route('/inventory_management_demo/overview', methods=['GET', 'POST'])	
@login_required
def inventory_management_demo():
	company = Company.query.filter_by(id=1).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	select_dept = company.departments.order_by(Department.name.asc())
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	is_super_admin = company.is_super_admin(user)
	my_supplies = MySupplies.query.filter_by(company_id=company.id, active=True).all()
	for my_s in my_supplies:
		my_s.current_quantity = Item.query.filter_by(company_id=company.id, product_id=my_s.product_id, date_used=None).count()
		my_s.less_quantity = my_s.min_quantity >= my_s.current_quantity
		my_s.item_query = Item.query.filter_by(company_id=company.id, product_id=my_s.product_id, date_used=None).all()
		for i in my_s.item_query:
			i.min_expiry = datetime.utcnow() + timedelta(days=my_s.min_expiry)
			i.greater_expiry =  (i.lot.expiry < i.min_expiry)
			i.quantity_dept = Item.query.filter_by(lot_id=i.lot_id, product_id=my_s.product_id, company_id=company.id, department_id=i.department_id, date_used=None).count()
	pending_deliveries = Purchase.query.filter(Purchase.date_purchased.isnot(None)).filter_by(company_id=company.id, delivery=None).all()
	delivered_purchases = Delivery.query.filter_by(company_id=company.id).all()
	for dp in delivered_purchases:
		dp.purchase_list = PurchaseList.query.filter_by(company_id=company.id, purchase_id=dp.purchase_id, date_cancelled=None).all()
		for pl in dp.purchase_list:
			pl.delivered_qty = Item.query.filter_by(purchase_list_id=pl.id).count()
			pl.dept_name = Department.query.filter_by(id=pl.department_id).first().name
	unsubmitted_orders = Order.query.filter(Order.date_submitted.isnot(None)).filter_by(puchase_no=None, company_id=company.id).all()
	pending_purchases = Purchase.query.filter_by(company_id=company.id, date_purchased=None).all()
	return render_template('inventory_management/inventory_overview.html', title='Inventory Demo', company=company, user=user, superuser=superuser, is_super_admin=is_super_admin, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor, my_supplies=my_supplies, unsubmitted_orders=unsubmitted_orders, pending_purchases=pending_purchases, purchases=purchases, pending_deliveries=pending_deliveries, delivered_purchases=delivered_purchases, select_dept=select_dept)	
	

#------------------------------------------------------------------------------------------#	
@app.route('/<company_name>/inventory_management/overview', methods=['GET', 'POST'])	
@login_required
def inventory_management(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	select_dept = company.departments.order_by(Department.name.asc())
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	is_super_admin = company.is_super_admin(user)
	if company.id is not 1:
		is_my_affiliate = company.is_my_affiliate(user)
		if not is_my_affiliate:
			return redirect(url_for('company', company_name=company.company_name))
	my_supplies = MySupplies.query.filter_by(company_id=company.id, active=True).all()
	for my_s in my_supplies:
		my_s.current_quantity = Item.query.filter_by(company_id=company.id, product_id=my_s.product_id, date_used=None).count()
		my_s.less_quantity = my_s.min_quantity >= my_s.current_quantity
		my_s.item_query = Item.query.filter_by(company_id=company.id, product_id=my_s.product_id, date_used=None).all()
		for i in my_s.item_query:
			i.min_expiry = datetime.utcnow() + timedelta(days=my_s.min_expiry)
			i.greater_expiry =  (i.lot.expiry < i.min_expiry)
			i.quantity_dept = Item.query.filter_by(lot_id=i.lot_id, product_id=my_s.product_id, company_id=company.id, department_id=i.department_id, date_used=None).count()
	pending_deliveries = Purchase.query.filter(Purchase.date_purchased.isnot(None)).filter_by(company_id=company.id, delivery=None).all()
	delivered_purchases = Delivery.query.filter_by(company_id=company.id).all()
	for dp in delivered_purchases:
		dp.purchase_list = PurchaseList.query.filter_by(company_id=company.id, purchase_id=dp.purchase_id, date_cancelled=None).all()
		for pl in dp.purchase_list:
			pl.delivered_qty = Item.query.filter_by(purchase_list_id=pl.id).count()
			pl.dept_name = Department.query.filter_by(id=pl.department_id).first().name
	unsubmitted_orders = Order.query.filter(Order.date_submitted.isnot(None)).filter_by(puchase_no=None, company_id=company.id).all()
	pending_purchases = Purchase.query.filter_by(company_id=company.id, date_purchased=None).all()
	return render_template('inventory_management/inventory_overview.html', title='Inventory Overview', company=company, user=user, superuser=superuser, is_super_admin=is_super_admin, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor, my_supplies=my_supplies, unsubmitted_orders=unsubmitted_orders, pending_purchases=pending_purchases, purchases=purchases, pending_deliveries=pending_deliveries, delivered_purchases=delivered_purchases, select_dept=select_dept)	


@app.route('/<company_name>/inventory_management/supplies', methods=['GET', 'POST'])
@login_required
def supplies(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	if company.id is not 1:
		is_my_affiliate = company.is_my_affiliate(user)
		if not is_my_affiliate:
			return redirect(url_for('company', company_name=company.company_name))
	#select_dept = company.departments.order_by(Department.name.asc())
	select_supplier = company.suppliers.order_by(Supplier.name.asc())
	#dept = company.departments
	#dept_list = [(d.id, d.name) for d in dept]
	#type = company.types
	#type_list = [(t.id, t.name) for t in type]
	supplier = company.suppliers
	supplier_list = [(s.id, s.name) for s in supplier]
	form = ProductRegistrationForm()
	#form.department.choices = dept_list
	#form.type.choices = type_list
	form.supplier.choices = supplier_list
	if form.validate_on_submit():
		raw_refnum = form.reference_number.data
		alnum_refnum = ''.join(e for e in raw_refnum if e.isalnum())
		prod = Product.query.filter_by(ref_number=alnum_refnum).first()
		if prod:
			my_prod = MySupplies.query.filter_by(product_id=prod.id, company_id=company.id, supplier_id=form.supplier.data).first()
			if my_prod:
				flash('Product already registered with same supplier.')
			else:
				p = MySupplies(company_id=company.id, product_id=prod.id, price=form.price.data, min_expiry=form.min_expiry.data, min_quantity=form.min_quantity.data, supplier_id=form.supplier.data, user_id=current_user.id)
				db.session.add(p)
				db.session.commit()
			return redirect(url_for('supplies', company_name=company.company_name))	
		else:
			product = Product(ref_number=alnum_refnum, name=form.name.data, description=form.description.data, storage_req=form.storage_req.data, type=form.type.data, user_id=current_user.id)
			db.session.add(product)
			db.session.commit()
			p = MySupplies(company_id=company.id, product_id=product.id, price=form.price.data, supplier_id=form.supplier.data, min_expiry=form.min_expiry.data, min_quantity=form.min_quantity.data, user_id=current_user.id)
			db.session.add(p)
			db.session.commit()
		return redirect(url_for('supplies', company_name=company.company_name))
	products = Product.query.order_by(Product.name.asc()).all()
	prod_type = Product.query.with_entities(Product.type).distinct()
	my_supplies = MySupplies.query.filter_by(company_id=company.id).all()
	for my_s in my_supplies:
		my_s.name = Product.query.filter_by(id=my_s.product_id).first().name
		my_s.ref_number = Product.query.filter_by(id=my_s.product_id).first().ref_number
		my_s.description = Product.query.filter_by(id=my_s.product_id).first().description
		my_s.storage_req = Product.query.filter_by(id=my_s.product_id).first().storage_req
		my_s.type = Product.query.filter_by(id=my_s.product_id).first().type
		my_s.supplier_name = Supplier.query.filter_by(id=my_s.supplier_id).first().name
	return render_template('inventory_management/supplies.html', title='Manage Supplies', description="Manage clinical laboratory supplies, encode supplies data that are used by your clinical laboratory.", user=user, superuser=superuser, form=form, products=products, company=company, is_super_admin=is_super_admin, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor, my_supplies=my_supplies, select_supplier=select_supplier, prod_type=prod_type)


@app.route('/<company_name>/inventory_management/link_supplies/<int:dept_id>', methods=['GET', 'POST'])
@login_required
def link_supplies(company_name, dept_id):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	if company.id is not 1:
		is_my_affiliate = company.is_my_affiliate(user)
		if not is_my_affiliate:
			return redirect(url_for('company', company_name=company.company_name))
	department = Department.query.filter_by(id=dept_id).first()
	my_supplies = MySupplies.query.filter_by(company_id=company.id, active=True).all()
	my_department_supplies = MyDepartmentSupplies.query.filter_by(company_id=company.id, department_id=department.id).all()
	linked_supply = False
	for my_s in my_supplies:
		my_s.name = Product.query.filter_by(id=my_s.product_id).first().name
		my_s.ref_number = Product.query.filter_by(id=my_s.product_id).first().ref_number
		my_s.description = Product.query.filter_by(id=my_s.product_id).first().description
		my_s.storage_req = Product.query.filter_by(id=my_s.product_id).first().storage_req
		my_s.type = Product.query.filter_by(id=my_s.product_id).first().type
		my_s.supplier_name = Supplier.query.filter_by(id=my_s.supplier_id).first().name
		my_s.department_supply = MyDepartmentSupplies.query.filter_by(company_id=company.id, department_id=department.id, my_supplies_id=my_s.id).first()
		my_s.linked_supply = False
		if my_s.department_supply:
			my_s.linked_supply = True
	return render_template('inventory_management/link_supplies.html', title='Link Supplies', user=user, superuser=superuser, company=company, is_super_admin=is_super_admin, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor, my_supplies=my_supplies, department=department)

@app.route('/<company_name>/inventory_management/link_supplies_to_department/<int:dept_id>/<int:supply_id>', methods=['GET', 'POST'])
@login_required
def link_supplies_to_department(company_name, dept_id, supply_id):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	if company.id is not 1:
		is_my_affiliate = company.is_my_affiliate(user)
		if not is_my_affiliate:
			return redirect(url_for('company', company_name=company.company_name))
	department = Department.query.filter_by(id=dept_id).first()
	my_department_supplies = MyDepartmentSupplies(company_id=company.id, my_supplies_id=supply_id, department_id=dept_id, user_id=current_user.id)
	db.session.add(my_department_supplies)
	db.session.commit()
	flash('Product has been added to ' + department.name + ' department.')
	return redirect(url_for('link_supplies', company_name=company.company_name, dept_id=dept_id))

@app.route('/<company_name>/edit_my_product/<ref_number>/<int:id>', methods=['GET', 'POST'])	
@login_required	
def edit_my_product(company_name, ref_number, id):
	product = Product.query.filter_by(ref_number=ref_number).first()
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	my_supplies = MySupplies.query.filter_by(company_id=company.id, product_id=product.id, id=id).first()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	if company.id is not 1:
		is_my_affiliate = company.is_my_affiliate(user)
		if not is_my_affiliate:
			return redirect(url_for('company', company_name=company.company_name))
	#dept = company.departments
	#dept_list = [(d.id, d.name) for d in dept]
	#type = company.types
	#type_list = [(t.id, t.name) for t in type]
	supplier = company.suppliers
	supplier_list = [(s.id, s.name) for s in supplier]
	#form.department.choices = dept_list
	#form.type.choices = type_list
	form = EditProductForm()
	form.supplier.choices = supplier_list
	if form.validate_on_submit():
		my_supplies.price = form.price.data
		my_supplies.active = form.active.data
		my_supplies.min_expiry = form.min_expiry.data
		my_supplies.min_quantity = form.min_quantity.data
		my_supplies.supplier_id = form.supplier.data
		#my_product.department_id = form.department.data
		#my_product.type_id = form.type.data
		db.session.commit()
		return redirect(url_for('supplies', company_name=company.company_name))	
	elif request.method == 'GET':
		form.price.data = my_supplies.price
		form.active.data = my_supplies.active
		form.min_expiry.data = my_supplies.min_expiry
		form.min_quantity.data = my_supplies.min_quantity
		form.supplier.data = my_supplies.supplier_id
		#form.department.data = my_product.department_id
		#form.type.data = my_product.type_id	
	return render_template('inventory_management/edit_product.html', title='Edit Products', user=user, superuser=superuser, form=form, product=product, company=company, is_super_admin=is_super_admin, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor)
	

@app.route('/<company_name>/delete_product/<ref_number>/<int:id>')	
@login_required	
def delete_product(company_name, ref_number, id):
	product = Product.query.filter_by(ref_number=ref_number).first()
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	my_supply = MySupplies.query.filter_by(company_id=company.id, product_id=product.id, id=id).first()
	db.session.delete(my_supply)
	db.session.commit()
	flash('Product has been deleted.')
	return redirect(url_for('supplies', company_name=company.company_name))	


@app.route('/<company_name>/inventory_management/inventory', methods=['GET', 'POST'])
@login_required
def inventory(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	orders = Order.query.filter_by(company_id=company.id).first()
	is_super_admin = company.is_super_admin(user)
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	if company.id is not 1:
		is_my_affiliate = company.is_my_affiliate(user)
		if not is_my_affiliate:
			return redirect(url_for('company', company_name=company.company_name))
	dept = company.departments.order_by(Department.name.asc())
	products = Product.query.order_by(Product.name.asc())
	my_supplies = MySupplies.query.filter_by(company_id=company.id, active=True).all()
	for my_s in my_supplies:
		my_s.item_query = Item.query.filter_by(my_supplies_id=my_s.id, company_id=company.id, date_used=None).all()
		for i in my_s.item_query:
			i.quantity_dept = Item.query.filter_by(lot_id=i.lot_id, product_id=my_s.product_id, company_id=company.id, department_id=i.department_id, date_used=None).count()
			i.min_expiry = datetime.utcnow() + timedelta(days=my_s.min_expiry)
			i.greater_expiry =  (i.lot.expiry < i.min_expiry)
	return render_template('inventory_management/inventory.html', title='Inventory', user=user, superuser=superuser, company=company, is_super_admin=is_super_admin,  is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor, my_supplies=my_supplies, orders=orders, dept=dept)

@app.route('/<company_name>/consume_item/<ref_number>/<id>', methods=['GET', 'POST'])
@login_required	
def consume_item(company_name, ref_number, id):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	is_super_admin = company.is_super_admin(user)
	if company.id is not 1:
		is_my_affiliate = company.is_my_affiliate(user)
		if not is_my_affiliate:
			return redirect(url_for('company', company_name=company.company_name))
	product = Product.query.filter_by(ref_number=ref_number).first()
	min_expiry = MySupplies.query.filter_by(id=id, product_id=product.id, company_id=company.id, active=True).first().min_expiry
	#product_id = Product.query.filter_by(ref_number=ref_number).first().id
	item_query = Item.query.filter_by(my_supplies_id=id, product_id=product.id, company_id=company.id, date_used=None).all()
	for i in item_query:
		i.lot_num = Lot.query.filter_by(id=i.lot_id).first().lot_no
		i.expiry = Lot.query.filter_by(id=i.lot_id).first().expiry
		i.datas = str(i.lot_num) + " - " + str(i.seq_no) +  " / " + str(i.expiry.strftime('%d-%m-%Y'))
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
	return render_template('inventory_management/consume.html', title='Consume supply', user=user, superuser=superuser, company=company, is_super_admin=is_super_admin, product=product, item_query=item_query, form=form)
	
@app.route('/<company_name>/inventory_management/internal', methods=['GET', 'POST'])
@login_required
def internal(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	is_super_admin = company.is_super_admin(user)
	if company.id is not 1:
		is_my_affiliate = company.is_my_affiliate(user)
		if not is_my_affiliate:
			return redirect(url_for('company', company_name=company.company_name))
	form = InternalRequestForm()
	dept = company.departments
	dept_list = [(d.id, d.name) for d in dept]
	form.from_department.choices = dept_list
	form.to_department.choices = dept_list
	if form.validate_on_submit():
		from_dept = Department.query.filter_by(id=form.from_department.data).first()
		#to_dept = Department.query.filter_by(id=form.to_department.data).first()
		request_n = from_dept.abbrv + "-" + datetime.utcnow().strftime('%Y-%m-%d-%H%M%S')
		internal_request = InternalRequest(request_no=request_n, company_id=company.id, from_dept=form.from_department.data, to_dept=form.to_department.data)
		db.session.add(internal_request)
		internal_request.internal_request_creator.append(user)
		db.session.commit()
		return redirect (url_for('create_internal_request', company_name=company.company_name, request_no=internal_request.request_no))
	internal_requests = InternalRequest.query.filter_by(company_id=company.id).order_by(InternalRequest.date_created.desc()).all()
	for r in internal_requests:
		n = 0
		r.internal_request_complete = False
		for l in r.request_list:
			if l.received_quantity is None:
				l.received_quantity = 0;
			if l.supplied_quantity is None:
				l.supplied_quantity = 0;
			if l.received_quantity >= l.supplied_quantity:
				n += 1
			if len(r.request_list) == n:
				r.internal_request_complete = True
			print(r.internal_request_complete, l.id, len(r.request_list), n)
	return render_template('inventory_management/internal.html', title='Internal', user=user, superuser=superuser, company=company, is_super_admin=is_super_admin, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor, form=form, internal_requests=internal_requests)
	
@app.route('/<company_name>/inventory_management/create_internal_request/<request_no>', methods=['GET', 'POST'])
@login_required
def create_internal_request(company_name, request_no):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	internal_request = InternalRequest.query.filter_by(request_no=request_no, company_id=company.id).first_or_404()
	request_list = InternalRequestList.query.filter_by(internal_request_id=internal_request.id, company_id=company.id).all()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	if company.id is not 1:
		is_my_affiliate = company.is_my_affiliate(user)
		if not is_my_affiliate:
			return redirect(url_for('company', company_name=company.company_name))
	dept = company.departments.order_by(Department.name.asc())
	from_dept_abbrv = Department.query.filter_by(id=internal_request.from_dept).first().abbrv
	to_dept_abbrv = Department.query.filter_by(id=internal_request.to_dept).first().abbrv
	my_supplies = MySupplies.query.filter_by(company_id=company.id, active=True).all()
	for my_s in my_supplies:
		my_s.from_item_count = Item.query.filter_by(my_supplies_id=my_s.id, product_id=my_s.product_id, company_id=company.id, department_id=internal_request.from_dept, date_used=None).count()
		my_s.to_item_count = Item.query.filter_by(my_supplies_id=my_s.id, product_id=my_s.product_id, company_id=company.id, department_id=internal_request.to_dept, date_used=None).count()
		my_s.from_dept = MyDepartmentSupplies.query.filter_by(company_id=company.id, my_supplies_id=my_s.id, department_id=internal_request.from_dept).all()
		'''my_s.to_dept = MyDepartmentSupplies.query.filter_by(company_id=company.id, my_supplies_id=my_s.id, department_id=internal_request.to_dept).all()
		for fd in my_s.from_dept:
			#my_ds.department = Department.query.filter_by(id=my_ds.department_id).first()
			fd.item_count = Item.query.filter_by(my_supplies_id=my_s.id, product_id=my_s.product_id, company_id=company.id, department_id=my_ds.department_id, date_used=None).count()'''
	for list in request_list:
		list.requested_by = User.query.filter_by(id=list.user_id).first().username
		list.from_item_count = Item.query.filter_by(my_supplies_id=list.my_supplies_id, company_id=company.id, department_id=internal_request.from_dept, date_used=None).count()
		list.to_item_count = Item.query.filter_by(my_supplies_id=list.my_supplies_id, company_id=company.id, department_id=internal_request.to_dept, date_used=None).count()
		list.lot_list = Item.query.filter_by(my_supplies_id=list.my_supplies_id, company_id=company.id, department_id=internal_request.to_dept, date_used=None).all()
		for i in list.lot_list:
			i.lot_num = Lot.query.filter_by(id=i.lot_id).first().lot_no
			i.expiry = Lot.query.filter_by(id=i.lot_id).first().expiry
	form = OrderListForm()
	if form.save.data:
		supply_id_list = request.form.getlist('supply_id')
		refnum_list = request.form.getlist('refnum')
		name_list = request.form.getlist('name')
		qty_list = request.form.getlist('qty')
		for i in range(0, len(refnum_list) ):
			list = InternalRequestList(ref_number=refnum_list[i], name=name_list[i], quantity=qty_list[i], my_supplies_id=supply_id_list[i], internal_request_id=internal_request.id, user_id=user.id, company_id=company.id)
			db.session.add(list)
			db.session.commit()
		return redirect (url_for('create_internal_request', company_name=company.company_name, request_no=internal_request.request_no))
	if form.submit.data:
		internal_request.request_submitted_by.append(user)
		internal_request.date_submitted = datetime.utcnow()
		db.session.commit()
		return redirect (url_for('internal', company_name=company.company_name))
	form2 = InternalRequestTransferForm()
	if form2.transfer.data:
		list_id = request.form.getlist('list_id')
		transfer_qty = request.form.getlist('transfer_qty')
		internal_request.date_transferred = datetime.utcnow()
		db.session.commit()
		for i in range(0, len(list_id) ):
			list_i = InternalRequestList.query.filter_by(id=list_id[i]).first()
			list_i.request_transferred_by.append(user)
			list_i.supplied_quantity = transfer_qty[i]
			list_i.date_transferred = datetime.utcnow()
			db.session.commit()
		return redirect (url_for('create_internal_request', company_name=company.company_name, request_no=internal_request.request_no))
	return render_template('inventory_management/create_internal_request.html', title='Create Requests', user=user, superuser=superuser, company=company, my_supplies=my_supplies, is_super_admin=is_super_admin, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor, internal_request=internal_request, request_list=request_list, form=form, form2=form2, dept=dept, from_dept_abbrv=from_dept_abbrv, to_dept_abbrv=to_dept_abbrv)
	
'''@app.route('/<company_id>/<request_no>/transfer_item/<int:irl_id>', methods=['GET', 'POST'])
@login_required	
def transfer_item(company_id, request_no, irl_id):
	company = Company.query.filter_by(id=company_id).first_or_404()
	internal_request = InternalRequest.query.filter_by(request_no=request_no, company_id=company.id).first_or_404()
	irl_item = InternalRequestList.query.filter_by(id=irl_id).first()
	#irl_item.date_transferred = datetime.utcnow()
	#irl_item.supplied_quantity = qty
	#irl_item.request_transferred_by.append(current_user)
	#db.session.commit()
	qty = request.form.get('transfer_qty_' + str(irl_id))
	print(qty)
	return redirect (url_for('create_internal_request', company_name=company.company_name, request_no=internal_request.request_no))'''
	
@app.route('/<company_id>/<request_no>/receive_item/<int:irl_id>/<int:item_id>')
@login_required	
def receive_item(company_id, request_no, irl_id, item_id):
	company = Company.query.filter_by(id=company_id).first_or_404()
	internal_request = InternalRequest.query.filter_by(request_no=request_no, company_id=company.id).first_or_404()
	irl_item = InternalRequestList.query.filter_by(id=irl_id).first()
	item = Item.query.filter_by(id=item_id).first()
	if irl_item.received_quantity is None:
		irl_item.received_quantity = 1
	else:
		irl_item.received_quantity += 1
	irl_item.date_received = datetime.utcnow()
	irl_item.request_received_by.append(current_user)
	item.department_id = internal_request.from_dept
	db.session.commit()
	return redirect (url_for('create_internal_request', company_name=company.company_name, request_no=internal_request.request_no))
	
@app.route('/<company_name>/<request_no>/remove_request_item/<int:id>')
@login_required	
def remove_request_item(company_name, request_no, id):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	internal_request = InternalRequest.query.filter_by(request_no=request_no, company_id=company.id).first_or_404()
	item = InternalRequestList.query.filter_by(id=id, company_id=company.id).first()
	db.session.delete(item)
	db.session.commit()
	return redirect (url_for('create_internal_request', company_name=company.company_name, request_no=internal_request.request_no))

@app.route('/<company_name>/inventory_management/orders', methods=['GET', 'POST'])
@login_required
def orders(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	orders = Order.query.filter_by(company_id=company.id).order_by(Order.date_created.desc()).all()
	for order in orders:
		order.purchase_order = Purchase.query.filter_by(order_id=order.id, company_id=company.id).first()
	purchases = Purchase.query.filter_by(company_id=company.id).all()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	is_super_admin = company.is_super_admin(user)
	if company.id is not 1:
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
		order_n = dept.abbrv + "-" + datetime.utcnow().strftime('%Y-%m-%d-%H%M%S')
		order = Order(order_no=order_n, company_id=company.id, department_id=dept.id)
		db.session.add(order)
		order.order_creator.append(user)
		db.session.commit()
		return redirect (url_for('create_orders', company_name=company.company_name, order_no=order.order_no))
	if form1.validate_on_submit():
		order = Order.query.filter_by(order_no=form1.order_no_purchase_form.data, company_id=company.id).first()
		purchase = Purchase(purchase_order_no=form1.purchase_order.data, company_id=company.id, order_id=order.id)
		db.session.add(purchase)
		purchase.purchase_created_by.append(user)
		db.session.commit()
		purchase_list = OrdersList.query.filter_by(order_id=order.id, company_id=company.id).all()
		for i in purchase_list:
			i.my_supply = MySupplies.query.filter_by(id=i.my_supplies_id).first()
			i.total = i.my_supply.price*i.quantity
			list = PurchaseList(ref_number=i.ref_number, name=i.name, price=i.my_supply.price, quantity=i.quantity, total=i.total, supplier_id=i.supplier_id, purchase_id=purchase.id, user_id=i.user_id, company_id=company.id, department_id=order.department_id, my_supplies_id=i.my_supplies_id)
			db.session.add(list)
			db.session.commit()
		return redirect (url_for('purchases', company_name=company.company_name))
	return render_template('inventory_management/orders.html', title='Orders', user=user, superuser=superuser, company=company, form=form, form1=form1, orders=orders, is_super_admin=is_super_admin, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor, purchases=purchases)



@app.route('/<company_name>/inventory_management/create_orders/<order_no>', methods=['GET', 'POST'])
@login_required
def create_orders(company_name, order_no):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	order = Order.query.filter_by(order_no=order_no, company_id=company.id).first_or_404()
	order_list = OrdersList.query.filter_by(order_id=order.id, company_id=company.id).all()
	#for list in order_list:
		#list.user = User.query.filter_by(id=list.user_id).first()
		#list.supplier = Supplier.query.filter_by(id=list.supplier_id).first().name
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	if company.id is not 1:
		is_my_affiliate = company.is_my_affiliate(user)
		if not is_my_affiliate:
			return redirect(url_for('company', company_name=company.company_name))
	#dept = company.departments.order_by(Department.name.asc())
	dept = Department.query.filter_by(id=order.department_id).first()
	products = Product.query.order_by(Product.name.asc())
	my_supplies = MySupplies.query.filter_by(company_id=company.id, active=True).all()
	for my_s in my_supplies:
		my_s.name = Product.query.filter_by(id=my_s.product_id).first().name
		my_s.ref_number = Product.query.filter_by(id=my_s.product_id).first().ref_number
		my_s.description = Product.query.filter_by(id=my_s.product_id).first().description
		my_s.dept_id = MyDepartmentSupplies.query.filter_by(company_id=company.id, my_supplies_id=my_s.id).all()
		for my_ds in my_s.dept_id:
			my_ds.department = Department.query.filter_by(id=my_ds.department_id).first()
			my_ds.item_count = Item.query.filter_by(my_supplies_id=my_s.id, product_id=my_s.product_id, company_id=company.id, department_id=my_ds.department_id, date_used=None).count()
		my_s.supplier = Supplier.query.filter_by(id=my_s.supplier_id).first()
		my_s.item_count = Item.query.filter_by(my_supplies_id=my_s.id, product_id=my_s.product_id, company_id=company.id, date_used=None).count()
	form = OrderListForm()
	if form.save.data:
		supply_id_list = request.form.getlist('supply_id')
		refnum_list = request.form.getlist('refnum')
		name_list = request.form.getlist('name')
		qty_list = request.form.getlist('qty')
		supplier_list = request.form.getlist('supplier')
		for i in range(0, len(refnum_list) ):
			list = OrdersList(ref_number=refnum_list[i], name=name_list[i], quantity=qty_list[i], my_supplies_id=supply_id_list[i], supplier_id=supplier_list[i],order_id=order.id, user_id=user.id, company_id=company.id, department_id=order.department_id)
			db.session.add(list)
			db.session.commit()
		return redirect (url_for('create_orders', company_name=company.company_name, order_no=order.order_no))
	if form.submit.data:
		order.order_submitted_by.append(user)
		order.date_submitted = datetime.utcnow()
		db.session.commit()
		return redirect (url_for('orders', company_name=company.company_name))
	return render_template('inventory_management/create_orders.html', title='Create Orders', user=user, superuser=superuser, company=company, products=products, my_supplies=my_supplies, order=order, is_super_admin=is_super_admin, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor, order_list=order_list, form=form, dept=dept)	


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
	superuser = User.query.filter_by(id=1).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	is_inv_admin = company.is_inv_admin(user)
	if company.id is not 1:
		is_my_affiliate = company.is_my_affiliate(user)
		if not is_my_affiliate:
			return redirect(url_for('company', company_name=company.company_name))
	purchases = Purchase.query.filter_by(company_id=company.id).order_by(Purchase.date_created.desc()).all()
	for purchase in purchases:
		purchase.delivered_purchases = Delivery.query.filter_by(purchase_id=purchase.id, company_id=company.id).all()
		purchase.purchase_list = PurchaseList.query.filter_by(purchase_id=purchase.id, company_id=company.id, date_cancelled=None).all()
		purchase.purchase_order_complete = False
		completed_item = 0
		for list in purchase.purchase_list:
			list.delivered_qty = Item.query.filter_by(purchase_list_id=list.id, company_id=company.id).count()
			#list.complete_item_delivery = list.delivered_qty == list.quantity
		for n in range(0, len(purchase.purchase_list)):
			if list.delivered_qty == list.quantity:
				completed_item += 1
		if len(purchase.purchase_list) == completed_item:
			purchase.purchase_order_complete = True
	#form = CreatePurchaseOrderForm()
	#for purchase in purchases:
	#	purchase.purchase_created_by = User.query.filter_by(id=purchase.created_by).first().username
	return render_template('inventory_management/purchases.html', title='Purchases', user=user, superuser=superuser, company=company, purchases=purchases, is_super_admin=is_super_admin, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor)		


@app.route('/<company_name>/inventory_management/purchase_list/<purchase_order_no>', methods=['GET', 'POST'])
@login_required
def purchase_list(company_name, purchase_order_no):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	purchase = Purchase.query.filter_by(purchase_order_no=purchase_order_no, company_id=company.id).first_or_404()
	purchase_list = PurchaseList.query.filter_by(purchase_id=purchase.id, company_id=company.id, date_cancelled=None).all()
	for list in purchase_list:
		#list.user = User.query.filter_by(id=list.user_id).first()
		list.product_id = Product.query.filter_by(ref_number=list.ref_number).first().id
		#list.supplier = Supplier.query.filter_by(id=list.supplier_id).first()
		#list.price = MySupplies.query.filter_by(id=list.my_supplies_id ,active=True).first().price
		#for s in list.supplier:
			#s.supplier_total_price += PurchaseList.query.filter_by(purchase_id=purchase.id, company_id=company.id).total()
		list.delivered_qty = Item.query.filter_by(purchase_list_id=list.id).count()
		list.cancelled_item = CancelledPurchaseListPending.query.filter_by(purchase_list_id=list.id).first() #cancelled with some items delivered
	cancelled_purchases = PurchaseList.query.filter(PurchaseList.date_cancelled.isnot(None)).filter_by(purchase_id=purchase.id, company_id=company.id).all() #cancelled without any item delivered
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	is_inv_admin = company.is_inv_admin(user)
	if company.id is not 1:
		is_my_affiliate = company.is_my_affiliate(user)
		if not is_my_affiliate:
			return redirect(url_for('company', company_name=company.company_name))
	#dept = company.departments.order_by(Department.name.asc())
	dept = Department.query.filter_by(id=purchase.order.department_id).first()
	supplier = company.suppliers.order_by(Supplier.name.asc())
	my_supplies = MySupplies.query.filter_by(company_id=company.id, active=True).all()
	for my_s in my_supplies:
		my_s.name = Product.query.filter_by(id=my_s.product_id).first().name
		my_s.ref_number = Product.query.filter_by(id=my_s.product_id).first().ref_number
		my_s.description = Product.query.filter_by(id=my_s.product_id).first().description
		#my_s.department = Department.query.filter_by(id=my_s.department_id).first().name
		my_s.supplier = Supplier.query.filter_by(id=my_s.supplier_id).first()
		my_s.dept_id = MyDepartmentSupplies.query.filter_by(company_id=company.id, my_supplies_id=my_s.id).all()
		for my_ds in my_s.dept_id:
			my_ds.department = Department.query.filter_by(id=my_ds.department_id).first()
			my_ds.item_count = Item.query.filter_by(my_supplies_id=my_s.id, product_id=my_s.product_id, company_id=company.id, department_id=my_ds.department_id, date_used=None).count()
		#my_s.item_count = Item.query.filter_by(product_id=my_s.product_id, company_id=company.id, date_used=None).count()
	form = OrderListForm()
	if form.save.data:
		supply_id_list = request.form.getlist('supply_id')
		refnum_list = request.form.getlist('refnum')
		name_list = request.form.getlist('name')
		price_list = request.form.getlist('price')
		qty_list = request.form.getlist('qty')
		tot_list = request.form.getlist('tot_price')
		supplier_list = request.form.getlist('supplier')
		#for i in refnum_list, price_list in range(0, len(refnum_list) ):
		for i in range(0, len(refnum_list) ):
			#print(refnum_list[i], name_list[i])
		#for refnum_list, name_list, price_list, qty_list, tot_list in range(0, len(refnum_list)):
			list = PurchaseList(ref_number=refnum_list[i], name=name_list[i], price=price_list[i], quantity=qty_list[i], total=tot_list[i], my_supplies_id=supply_id_list[i], supplier_id=supplier_list[i], department_id=purchase.order.department_id, purchase_id=purchase.id, user_id=user.id, company_id=company.id)
			db.session.add(list)
			db.session.commit()
		return redirect (url_for('purchase_list', company_name=company.company_name, purchase_order_no=purchase.purchase_order_no))
	if form.submit.data:
		subtotal = form.subtotal.data
		purchase.total = subtotal
		purchase.purchased_by.append(user)
		purchase.date_purchased = datetime.utcnow()
		db.session.commit()
		return redirect (url_for('purchases', company_name=company.company_name))
	#subtotal = form.subtotal.data
	#print(subtotal)
	return render_template('inventory_management/purchase_list.html', title='Purchase List', user=user, superuser=superuser, company=company, purchase=purchase, is_super_admin=is_super_admin, is_inv_supervisor=is_inv_supervisor, is_inv_admin=is_inv_admin, purchase_list=purchase_list, form=form, dept=dept, my_supplies=my_supplies, supplier=supplier, cancelled_purchases=cancelled_purchases)		


@app.route('/<company_name>/<purchase_order_no>/remove_purchase_item/<int:id>')
@login_required	
def remove_purchase_item(company_name, purchase_order_no, id):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	if company.id is not 1:
		is_my_affiliate = company.is_my_affiliate(user)
		if not is_my_affiliate:
			return redirect(url_for('company', company_name=company.company_name))
	purchase = Purchase.query.filter_by(purchase_order_no=purchase_order_no, company_id=company.id).first_or_404()
	item = PurchaseList.query.filter_by(id=id, company_id=company.id).first()
	db.session.delete(item)
	db.session.commit()
	return redirect (url_for('purchase_list', company_name=company.company_name, purchase_order_no=purchase.purchase_order_no))
	
@app.route('/<company_name>/<purchase_order_no>/cancel_purchased_item/<int:id>')
@login_required	
def cancel_purchased_item(company_name, purchase_order_no, id):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	if company.id is not 1:
		is_inv_admin = company.is_inv_admin(current_user)
		if not is_inv_admin:
			return redirect(url_for('company', company_name=company.company_name))
	purchase = Purchase.query.filter_by(purchase_order_no=purchase_order_no, company_id=company.id).first_or_404()
	item = PurchaseList.query.filter_by(id=id, company_id=company.id).first()
	item_query = Item.query.filter_by(purchase_list_id=item.id).first()
	if item_query is not None:
		flash("Cannot cancel item, already delivered")
		return redirect (url_for('purchase_list', company_name=company.company_name, purchase_order_no=purchase.purchase_order_no))
	else:
		item.date_cancelled = datetime.utcnow()
		db.session.commit()
		return redirect (url_for('purchase_list', company_name=company.company_name, purchase_order_no=purchase.purchase_order_no))
		
@app.route('/<company_name>/<purchase_order_no>/cancel_pending_item/<delivery_order_no>/<int:id>')
@login_required	
def cancel_pending_item(company_name, purchase_order_no, delivery_order_no, id):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	if company.id is not 1:
		is_inv_admin = company.is_inv_admin(current_user)
		if not is_inv_admin:
			return redirect(url_for('company', company_name=company.company_name))
	purchase = Purchase.query.filter_by(purchase_order_no=purchase_order_no, company_id=company.id).first_or_404()
	purchase_list = PurchaseList.query.filter_by(id=id, company_id=company.id).first()
	purchase_list_delivered_qty = Item.query.filter_by(purchase_list_id=purchase_list.id, company_id=company.id).count()
	cancelled_qty = purchase_list.quantity - purchase_list_delivered_qty
	if cancelled_qty <= 0:
		flash("Cannot cancel, items already delivered")
		return redirect(url_for('accept_delivery', company_name=company.company_name, purchase_order_no=purchase_order_no, delivery_order_no=delivery_order_no))
	else:
		cancelled_item = CancelledPurchaseListPending(cancelled_qty=cancelled_qty, purchase_list_id=purchase_list.id, cancelled_by=current_user.id)
		db.session.add(cancelled_item)
		db.session.commit()
		return redirect(url_for('accept_delivery', company_name=company.company_name, purchase_order_no=purchase_order_no, delivery_order_no=delivery_order_no))
		

@app.route('/<company_name>/<purchase_order_no>/accept_delivery/<delivery_order_no>')
@login_required	
def accept_delivery(company_name, purchase_order_no, delivery_order_no):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	purchase = Purchase.query.filter_by(purchase_order_no=purchase_order_no, company_id=company.id).first_or_404()
	delivery = Delivery.query.filter_by(delivery_no=delivery_order_no, company_id=company.id).first_or_404()
	purchase_list = PurchaseList.query.filter_by(purchase_id=purchase.id, company_id=company.id, supplier_id=delivery.supplier_id, date_cancelled=None).all()
	d_supplier = Supplier.query.filter_by(id=delivery.supplier_id).first().name
	for list in purchase_list:
		list.delivered_qty = Item.query.filter_by(purchase_list_id=list.id, company_id=company.id).count()
		list.delivery_delivered_qty = Item.query.filter_by(purchase_list_id=list.id, company_id=company.id, delivery_id=delivery.id).count()
		list.cancelled_item = CancelledPurchaseListPending.query.filter_by(purchase_list_id=list.id).first()
		list.complete_delivery = list.delivered_qty >= list.quantity
		if list.cancelled_item:
			list.complete_delivery = list.delivered_qty >= (list.quantity - list.cancelled_item.cancelled_qty)
		list.item = Item.query.filter_by(purchase_list_id=list.id, company_id=company.id).all()
		list.delivery_no_list = []
		for l in list.item:
			l.delivery_no = Delivery.query.filter_by(id=l.delivery_id, company_id=company.id).first().delivery_no
			list.delivery_no_list.append(l.delivery_no)
		list.count_delivery_no_list = dict((x,list.delivery_no_list.count(x)) for x in set(list.delivery_no_list))	
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	is_inv_admin = company.is_inv_admin(user)
	if company.id is not 1:
		is_my_affiliate = company.is_my_affiliate(user)
		if not is_my_affiliate:
			return redirect(url_for('company', company_name=company.company_name))
	return render_template('inventory_management/accept_delivery.html', title='Accept Delivery', user=user, superuser=superuser, company=company, purchase=purchase, is_super_admin=is_super_admin, is_inv_supervisor=is_inv_supervisor, is_inv_admin=is_inv_admin, purchase_list=purchase_list, delivery=delivery, d_supplier=d_supplier)		


@app.route('/<company_name>/<purchase_order_no>/receive_delivery_item/<delivery_order_no>/<int:id>', methods=['GET', 'POST'])
@login_required	
def receive_delivery_item(company_name, purchase_order_no, delivery_order_no, id):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	purchase = Purchase.query.filter_by(purchase_order_no=purchase_order_no, company_id=company.id).first_or_404()
	order = Order.query.filter_by(id=purchase.order_id, company_id=company.id).first_or_404()
	purchased_item = PurchaseList.query.filter_by(id=id, company_id=company.id).first()
	delivery = Delivery.query.filter_by(delivery_no=delivery_order_no, company_id=company.id).first_or_404()
	product = Product.query.filter_by(ref_number=purchased_item.ref_number).first()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	is_super_admin = company.is_super_admin(user)
	if company.id is not 1:
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
			lot = Lot(lot_no=alnum_lotno, product_id=product.id, expiry=form.expiry.data, user_id=current_user.id)
			db.session.add(lot)
			db.session.commit()
			for i in range(0, qty):
				seq = Item.query.filter_by(lot_id=lot.id, company_id=company.id).count()
				seq += 1
				item = Item(lot_id=lot.id, seq_no=seq, company_id=company.id, product_id=product.id, purchase_list_id=id, department_id=order.department_id, supplier_id=purchased_item.supplier_id, delivery_id=delivery.id, my_supplies_id=purchased_item.my_supplies_id)
				db.session.add(item)
				#purchased_item.deliveries.append(delivery)
				db.session.commit()
			return redirect(url_for('accept_delivery', company_name=company.company_name, purchase_order_no=purchase.purchase_order_no, delivery_order_no=delivery.delivery_no))
		if lot_query is not None:
			lot = Lot.query.filter_by(lot_no=alnum_lotno).first()
			seq = Item.query.filter_by(lot_id=lot.id, company_id=company.id).count()
			seq += 1
			for i in range(0, qty):
				item = Item(lot_id=lot.id, seq_no=seq, company_id=company.id, product_id=product.id, purchase_list_id=id, delivery_id=delivery.id, department_id=order.department_id, supplier_id=purchased_item.supplier_id, my_supplies_id=purchased_item.my_supplies_id)
				db.session.add(item)
				#purchased_item.deliveries.append(delivery)
				db.session.commit()
			return redirect(url_for('accept_delivery', company_name=company.company_name, purchase_order_no=purchase_order_no, delivery_order_no=delivery_order_no))
	return render_template('inventory_management/receive_delivery_item.html', title='Receive Item', user=user, superuser=superuser, company=company, purchase=purchase, is_super_admin=is_super_admin, purchased_item=purchased_item, form=form, delivery=delivery)	

	
@app.route('/<company_name>/inventory_management/deliveries', methods=['GET', 'POST'])
@login_required
def deliveries(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	purchases = Purchase.query.filter_by(company_id=company.id).order_by(Purchase.date_purchased.desc()).all()
	for purchase in purchases:
		purchase.delivered_purchases = Delivery.query.filter_by(purchase_id=purchase.id, company_id=company.id).all()
		purchase.purchase_list = PurchaseList.query.filter_by(purchase_id=purchase.id, company_id=company.id, date_cancelled=None).all()
		purchase.purchase_order_complete = False
		completed_item = 0
		for list in purchase.purchase_list:
			list.delivered_qty = Item.query.filter_by(purchase_list_id=list.id, company_id=company.id).count()
			#list.complete_item_delivery = list.delivered_qty == list.quantity
		for n in range(0, len(purchase.purchase_list)):
			if list.delivered_qty == list.quantity:
				completed_item += 1
		if len(purchase.purchase_list) == completed_item:
			purchase.purchase_order_complete = True
		#print(completed_item , len(purchase.purchase_list))
	is_super_admin = company.is_super_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	is_inv_admin = company.is_inv_admin(user)
	if company.id is not 1:
		is_my_affiliate = company.is_my_affiliate(user)
		if not is_my_affiliate:
			return redirect(url_for('company', company_name=company.company_name))
	form = AcceptDeliveryForm()
	suppliers = company.suppliers
	supplier_list = [(d.id, d.name) for d in suppliers]
	form.supplier.choices = supplier_list
	if form.validate_on_submit():
		purchase = Purchase.query.filter_by(purchase_order_no=form.purchase_no.data, company_id=company.id).first_or_404()
		dq = Delivery.query.filter_by(delivery_no=form.delivery_no.data, company_id=company.id).first()
		if dq is not None:
			flash('Delivery Number already registered! Please check that you have entered the correct data or add it to the existing one.')
		else:
			delivery = Delivery(delivery_no=form.delivery_no.data, receiver_id=user.id, company_id=company.id, purchase_id=purchase.id, supplier_id=form.supplier.data)
			db.session.add(delivery)
			db.session.commit()
			return redirect(url_for('accept_delivery', company_name=company.company_name, purchase_order_no=purchase.purchase_order_no, delivery_order_no=delivery.delivery_no))
	return render_template('inventory_management/deliveries.html', title='Deliveries', user=user, superuser=superuser, company=company, is_super_admin=is_super_admin, is_inv_supervisor=is_inv_supervisor, is_inv_admin=is_inv_admin, purchases=purchases, form=form)
	
@app.route('/<company_name>/inventory_management/suppliers',  methods=['GET', 'POST'])
@login_required
def suppliers(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	if company.id is not 1:
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
	return render_template('inventory_management/suppliers.html', title='Suppliers', user=user, superuser=superuser, form=form, suppliers=suppliers, company=company, is_super_admin=is_super_admin, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor)


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
	superuser = User.query.filter_by(id=1).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	if company.id is not 1:
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
	return render_template('inventory_management/departments.html', title='Departments', user=user, superuser=superuser, form1=form1, form2=form2, types=types, company=company, is_super_admin=is_super_admin, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor, departments=departments)

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
	
@app.route('/<company_name>/inventory_management/accounts',  methods=['GET', 'POST'])
@login_required
def inventory_accounts(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	if company.id is not 1:
		is_inv_admin = company.is_inv_admin(user)
		if not is_inv_admin:
			return redirect(url_for('company', company_name=company.company_name))
	return render_template('inventory_management/inventory_accounts.html', title='Accounts', is_super_admin=is_super_admin, company=company, user=user, superuser=superuser, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor)

@app.route('/<company_name>/inventory_management/accounts/total_purchases',  methods=['GET', 'POST'])
@login_required
def total_purchases_accounts(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	if company.id is not 1:
		is_my_affiliate = company.is_my_affiliate(user)
		if not is_my_affiliate:
			return redirect(url_for('company', company_name=company.company_name))
	dept = company.departments
	dept_list = [(0, 'All')] + [(d.id, d.name) for d in dept]
	supplier = company.suppliers
	supplier_list = [(0, 'All')] + [(s.id, s.name) for s in supplier]
	form = AccountsQueryForm()
	form.department.choices = dept_list
	form.supplier.choices = supplier_list
	purchases = ''
	if form.validate_on_submit():
		end_date = datetime.combine(form.end_date.data, time(23, 59, 59))
		if form.department.data == 0 and form.supplier.data == 0:
			purchases = Purchase.query.filter(Purchase.date_purchased.between(form.start_date.data, end_date)).filter_by(company_id=company.id).all()
			for purchase in purchases:
				purchase.purchase_list = PurchaseList.query.filter_by(purchase_id=purchase.id, date_cancelled=None).all()
				purchase.total_purchased = 0
				for p in purchase.purchase_list:
					p.cancelled_item = CancelledPurchaseListPending.query.filter_by(purchase_list_id=p.id).first()
					if p.cancelled_item:
						purchase.total_purchased += p.total - (p.cancelled_item.cancelled_qty * p.price)
					else:
						purchase.total_purchased += p.total
		elif form.department.data == 0 and form.supplier.data is not 0:
			purchases = Purchase.query.filter(Purchase.date_purchased.between(form.start_date.data, end_date)).filter_by(company_id=company.id).all()
			for purchase in purchases:
				purchase.purchase_list = PurchaseList.query.filter_by(purchase_id=purchase.id, supplier_id=form.supplier.data, date_cancelled=None).all()
				purchase.total_purchased = 0
				for p in purchase.purchase_list:
					p.cancelled_item = CancelledPurchaseListPending.query.filter_by(purchase_list_id=p.id).first()
					if p.cancelled_item:
						purchase.total_purchased += p.total - (p.cancelled_item.cancelled_qty * p.price)
					else:
						purchase.total_purchased += p.total
		elif form.supplier.data == 0 and form.department.data is not 0:
			purchases = Purchase.query.filter(Purchase.date_purchased.between(form.start_date.data, end_date)).filter_by(company_id=company.id).all()
			for purchase in purchases:
				purchase.purchase_list = PurchaseList.query.filter_by(purchase_id=purchase.id, department_id=form.department.data, date_cancelled=None).all()
				purchase.total_purchased = 0
				for p in purchase.purchase_list:
					p.cancelled_item = CancelledPurchaseListPending.query.filter_by(purchase_list_id=p.id).first()
					if p.cancelled_item:
						purchase.total_purchased += p.total - (p.cancelled_item.cancelled_qty * p.price)
					else:
						purchase.total_purchased += p.total
		elif form.supplier.data is not 0 and form.department.data is not 0:
			purchases = Purchase.query.filter(Purchase.date_purchased.between(form.start_date.data, end_date)).filter_by(company_id=company.id).all()
			for purchase in purchases:
				purchase.purchase_list = PurchaseList.query.filter_by(purchase_id=purchase.id, department_id=form.department.data, supplier_id=form.supplier.data, date_cancelled=None).all()
				purchase.total_purchased = 0
				for p in purchase.purchase_list:
					p.cancelled_item = CancelledPurchaseListPending.query.filter_by(purchase_list_id=p.id).first()
					if p.cancelled_item:
						purchase.total_purchased += p.total - (p.cancelled_item.cancelled_qty * p.price)
					else:
						purchase.total_purchased += p.total
	return render_template('inventory_management/total_purchases.html', title='Total Purchases', is_super_admin=is_super_admin, company=company, user=user, superuser=superuser, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor, form=form, purchases=purchases)


@app.route('/<company_name>/inventory_management/accounts/total_deliveries',  methods=['GET', 'POST'])
@login_required
def total_deliveries_accounts(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	if company.id is not 1:
		is_my_affiliate = company.is_my_affiliate(user)
		if not is_my_affiliate:
			return redirect(url_for('company', company_name=company.company_name))
	dept = company.departments
	dept_list = [(0, 'All')] + [(d.id, d.name) for d in dept]
	supplier = company.suppliers
	supplier_list = [(0, 'All')] + [(s.id, s.name) for s in supplier]
	form = AccountsQueryForm()
	form.department.choices = dept_list
	form.supplier.choices = supplier_list
	deliveries = Delivery.query.filter_by(company_id=company.id).all()
	purchases = ''		
	#total delivered prices are based on price from purchase list, i.e. the item price from when it was purchased, to avoid confusion if  prices change in the future
	if form.validate_on_submit():   
		end_date = datetime.combine(form.end_date.data, time(23, 59, 59))
		if form.department.data == 0 and form.supplier.data == 0:
			purchases = Purchase.query.filter(Purchase.date_purchased.between(form.start_date.data, end_date)).filter_by(company_id=company.id).all()
			for purchase in purchases:
				purchase.purchase_list = PurchaseList.query.filter_by(purchase_id=purchase.id, date_cancelled=None).all()
				purchase.total_purchased = 0
				for p in purchase.purchase_list:
					p.cancelled_item = CancelledPurchaseListPending.query.filter_by(purchase_list_id=p.id).first()
					if p.cancelled_item:
						purchase.total_purchased += p.total - (p.cancelled_item.cancelled_qty * p.price)
					else:
						purchase.total_purchased += p.total
				for p in purchase.delivery:
					p.delivery_list = Item.query.filter_by(delivery_id=p.id).all()
					p.delivery_total = 0
					for item in p.delivery_list:
						p.delivery_total += item.purchase_list_to_item.price
		elif form.department.data == 0 and form.supplier.data is not 0:
			purchases = Purchase.query.filter(Purchase.date_purchased.between(form.start_date.data, end_date)).filter_by(company_id=company.id).all()
			for purchase in purchases:
				purchase.purchase_list = PurchaseList.query.filter_by(purchase_id=purchase.id, supplier_id=form.supplier.data, date_cancelled=None).all()
				purchase.total_purchased = 0
				for p in purchase.purchase_list:
					p.cancelled_item = CancelledPurchaseListPending.query.filter_by(purchase_list_id=p.id).first()
					if p.cancelled_item:
						purchase.total_purchased += p.total - (p.cancelled_item.cancelled_qty * p.price)
					else:
						purchase.total_purchased += p.total
				for p in purchase.delivery:
					p.delivery_list = Item.query.filter_by(delivery_id=p.id, supplier_id=form.supplier.data).all()
					p.delivery_total = 0
					for item in p.delivery_list:
						p.delivery_total += item.purchase_list_to_item.price
		elif form.supplier.data == 0 and form.department.data is not 0:
			purchases = Purchase.query.filter(Purchase.date_purchased.between(form.start_date.data, end_date)).filter_by(company_id=company.id).all()
			for purchase in purchases:
				purchase.purchase_list = PurchaseList.query.filter_by(purchase_id=purchase.id, department_id=form.department.data, date_cancelled=None).all()
				purchase.total_purchased = 0
				for p in purchase.purchase_list:
					p.cancelled_item = CancelledPurchaseListPending.query.filter_by(purchase_list_id=p.id).first()
					if p.cancelled_item:
						purchase.total_purchased += p.total - (p.cancelled_item.cancelled_qty * p.price)
					else:
						purchase.total_purchased += p.total
				for p in purchase.delivery:
					p.delivery_list = Item.query.filter_by(delivery_id=p.id, department_id=form.department.data).all()
					p.delivery_total = 0
					for item in p.delivery_list:
						p.delivery_total += item.purchase_list_to_item.price
		elif form.supplier.data is not 0 and form.department.data is not 0:
			purchases = Purchase.query.filter(Purchase.date_purchased.between(form.start_date.data, end_date)).filter_by(company_id=company.id).all()
			for purchase in purchases:
				purchase.purchase_list = PurchaseList.query.filter_by(purchase_id=purchase.id, department_id=form.department.data, supplier_id=form.supplier.data, date_cancelled=None).all()
				purchase.total_purchased = 0
				for p in purchase.purchase_list:
					p.cancelled_item = CancelledPurchaseListPending.query.filter_by(purchase_list_id=p.id).first()
					if p.cancelled_item:
						purchase.total_purchased += p.total - (p.cancelled_item.cancelled_qty * p.price)
					else:
						purchase.total_purchased += p.total
				for p in purchase.delivery:
					p.delivery_list = Item.query.filter_by(delivery_id=p.id, department_id=form.department.data, supplier_id=form.supplier.data).all()
					p.delivery_total = 0
					for item in p.delivery_list:
						p.delivery_total += item.purchase_list_to_item.price
	return render_template('inventory_management/total_deliveries.html', title='Total Deliveries', is_super_admin=is_super_admin, company=company, user=user, superuser=superuser, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor, form=form, purchases=purchases)
	

@app.route('/<company_name>/inventory_management/accounts/total_inventory',  methods=['GET', 'POST'])
@login_required
def total_inventory_accounts(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	if company.id is not 1:
		is_my_affiliate = company.is_my_affiliate(user)
		if not is_my_affiliate:
			return redirect(url_for('company', company_name=company.company_name))
	dept = company.departments
	dept_list = [(0, 'All')] + [(d.id, d.name) for d in dept]
	supplier = company.suppliers
	supplier_list = [(0, 'All')] + [(s.id, s.name) for s in supplier]
	form = AccountsQueryForm()
	form.department.choices = dept_list
	form.supplier.choices = supplier_list
	my_supplies = ''
	if form.validate_on_submit():
		my_supplies = MySupplies.query.filter_by(company_id=company.id, active=True).all()
		end_date = datetime.combine(form.end_date.data, time(23, 59, 59))
		if form.department.data == 0 and form.supplier.data == 0:
			for my_s in my_supplies:
				removed_item = []
				for my_item in reversed(my_s.item):
					my_item.delivery_date = Delivery.query.filter_by(id = my_item.delivery_id).first()
					if my_item.delivery_date.date_delivered > end_date:
						my_s.item.remove(my_item)
						removed_item.append(my_item)
					if my_item.date_used is not None:
						if my_item.date_used <= end_date:
							removed_item.append(my_item)
							my_s.item.remove(my_item)
					my_s.count = len(my_s.item)
	#current total inventory price is set on current pricing since it measures the current value of total inventory
					#print(my_s.item)
					#print(my_item)
					#print(my_s.id, my_item, my_item.delivery_date, my_item.date_used)
					#print("removed_item:", removed_item)
		elif form.department.data == 0 and form.supplier.data is not 0:
			for my_s in my_supplies:
				my_s.item = Item.query.filter_by(my_supplies_id=my_s.id, supplier_id=form.supplier.data).all()
				for my_item in reversed(my_s.item):
					my_item.delivery_date = Delivery.query.filter_by(id = my_item.delivery_id).first().date_delivered
					if my_item.delivery_date > end_date:
						my_s.item.remove(my_item)
					if my_item.date_used is not None:
						if my_item.date_used <= end_date:
							my_s.item.remove(my_item)
					my_s.count = len(my_s.item)
		elif form.supplier.data == 0 and form.department.data is not 0:
			for my_s in my_supplies:
				my_s.item = Item.query.filter_by(my_supplies_id=my_s.id, department_id=form.department.data).all()
				for my_item in reversed(my_s.item):
					my_item.delivery_date = Delivery.query.filter_by(id = my_item.delivery_id).first().date_delivered
					if my_item.delivery_date > end_date:
						my_s.item.remove(my_item)
					if my_item.date_used is not None:
						if my_item.date_used <= end_date:
							my_s.item.remove(my_item)
					my_s.count = len(my_s.item)
		elif form.supplier.data is not 0 and form.department.data is not 0:
			for my_s in my_supplies:
				my_s.item = Item.query.filter_by(my_supplies_id=my_s.id, department_id=form.department.data, supplier_id=form.supplier.data).all()
				for my_item in reversed(my_s.item):
					my_item.delivery_date = Delivery.query.filter_by(id = my_item.delivery_id).first().date_delivered
					if my_item.delivery_date > end_date:
						my_s.item.remove(my_item)
					if my_item.date_used is not None:
						if my_item.date_used <= end_date:
							my_s.item.remove(my_item)
					my_s.count = len(my_s.item)
	return render_template('inventory_management/total_inventory_remaining.html', title='Total Deliveries', is_super_admin=is_super_admin, company=company, user=user, superuser=superuser, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor, form=form, my_supplies=my_supplies)

@app.route('/<company_name>/inventory_management/accounts/total_consumed',  methods=['GET', 'POST'])
@login_required
def total_consumed_accounts(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	is_super_admin = company.is_super_admin(user)
	is_inv_admin = company.is_inv_admin(user)
	is_inv_supervisor = company.is_inv_supervisor(user)
	if company.id is not 1:
		is_my_affiliate = company.is_my_affiliate(user)
		if not is_my_affiliate:
			return redirect(url_for('company', company_name=company.company_name))
	dept = company.departments
	dept_list = [(0, 'All')] + [(d.id, d.name) for d in dept]
	supplier = company.suppliers
	supplier_list = [(0, 'All')] + [(s.id, s.name) for s in supplier]
	form = AccountsQueryForm()
	form.department.choices = dept_list
	form.supplier.choices = supplier_list
	my_supplies = ''
	if form.validate_on_submit():
		my_supplies = MySupplies.query.filter_by(company_id=company.id, active=True).all()
		end_date = datetime.combine(form.end_date.data, time(23, 59, 59))
		if form.department.data == 0 and form.supplier.data == 0:
			for my_s in my_supplies:
				my_s.used_item = Item.query.filter(Item.date_used.between(form.start_date.data, end_date)).filter_by(my_supplies_id=my_s.id).all()
				my_s.count = len(my_s.used_item)
				for item in my_s.used_item:
					my_s.purchased_price = item.purchase_list_to_item.price
				#print(my_s.used_item, len(my_s.used_item))
		elif form.department.data == 0 and form.supplier.data is not 0:
			for my_s in my_supplies:
				my_s.used_item = Item.query.filter(Item.date_used.between(form.start_date.data, end_date)).filter_by(my_supplies_id=my_s.id, supplier_id=form.supplier.data).all()
				my_s.count = len(my_s.used_item)
		elif form.supplier.data == 0 and form.department.data is not 0:
			for my_s in my_supplies:
				my_s.used_item = Item.query.filter(Item.date_used.between(form.start_date.data, end_date)).filter_by(my_supplies_id=my_s.id, department_id=form.department.data).all()
				my_s.count = len(my_s.used_item)
		elif form.supplier.data is not 0 and form.department.data is not 0:
			for my_s in my_supplies:
				my_s.used_item = Item.query.filter(Item.date_used.between(form.start_date.data, end_date)).filter_by(my_supplies_id=my_s.id, department_id=form.department.data, supplier_id=form.supplier.data).all()
				my_s.count = len(my_s.used_item)
	return render_template('inventory_management/total_inventory_consumed.html', title='Inventory Consumed ', is_super_admin=is_super_admin, company=company, user=user, superuser=superuser, is_inv_admin=is_inv_admin, is_inv_supervisor=is_inv_supervisor, form=form, my_supplies=my_supplies)

@app.route('/products_wiki',  methods=['GET', 'POST'])
def products_wiki():
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	products = Product.query.all()
	return render_template('products_wiki.html', title='Products Wiki', user=user, superuser=superuser, products=products)


@app.route('/<company_name>/document_control/', methods=['GET', 'POST'])
@login_required
def document_control(company_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
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
			dept = DocumentationDepartment(department_name=form1.dept_name.data, department_abbrv=form1.dept_abbrv.data, company_id=company.id, user_id=current_user.id)
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
	return render_template('documentation_page/document_control.html', title='Document Control', user=user, superuser=superuser, company=company, is_super_admin=is_super_admin, is_doc_supervisor=is_doc_supervisor, is_doc_admin=is_doc_admin, is_my_affiliate=is_my_affiliate, form1=form1, form2=form2, departments=departments)

@app.route('/<company_name>/documents/<department_name>/<document_no>/<document_name>', methods=['GET', 'POST'])
@login_required
def documents(company_name, department_name, document_no, document_name):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	department = DocumentationDepartment.query.filter_by(company_id=company.id, department_name=department_name).first()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
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
	form3 = EditDocumentSectionForm()
	if form3.validate_on_submit():
		section = DocumentSection.query.get(form3.section_id.data)
		section.section_number = form3.edit_section_number.data
		section.section_title = form3.edit_section_title.data
		db.session.commit()
		return redirect(url_for('documents', company_name=company.company_name, department_name=department.department_name, document_no=document.document_no, document_name=document.document_name))
	elif request.method == 'GET':
		for sect in sections:
			form3.edit_section_number.data = sect.section_number
			form3.edit_section_title.data = sect.section_title
	form4 = DocumentSubmitForm()
	if form4.validate_on_submit():
		section_id_list = request.form.getlist('submit_section_id')
		section_body_id_list = request.form.getlist('submit_section_body_id')
		for i in range(0, len(section_id) ):
			version = DocumentVersion(section_id=section_id_list[i], section_body_id=section_body_id_list[i])
	return render_template('documentation_page/lab_document.html', user=user, company=company, superuser=superuser, is_super_admin=is_super_admin, is_my_affiliate=is_my_affiliate, department=department, document=document, sections=sections, form1=form1, form3=form3, form4=form4)
	

@app.route('/<company_name>/documents/<department_name>/<document_no>/<document_name>/<section_number>/<section_title>/edit', methods=['GET', 'POST'])
@login_required
def edit_section_body(company_name, department_name, document_no, document_name, section_number, section_title):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	department = DocumentationDepartment.query.filter_by(company_id=company.id, department_name=department_name).first()
	user = User.query.filter_by(username=current_user.username).first_or_404()
	superuser = User.query.filter_by(id=1).first_or_404()
	document = DocumentName.query.filter_by(company_id=company.id, document_no=document_no, document_name=document_name).first()
	section = DocumentSection.query.filter_by(company_id=company.id, department_id=department.id, document_name_id=document.id, section_number=section_number, section_title=section_title).first()
	section_body = DocumentSectionBody.query.filter_by(company_id=company.id, department_id=department.id, document_name_id=document.id, document_section_id=section.id).first()
	#section_body_id = DocumentSectionBody.query.get(section_body.id)
	is_super_admin = company.is_super_admin(user)
	is_my_affiliate = company.is_my_affiliate(user)
	if not is_my_affiliate:
		return redirect(url_for('company', company_name=company.company_name))
	form2 = EditDocumentBodyForm()
	if form2.validate_on_submit():
		body = DocumentSectionBody(section_body=form2.body.data, change_log=form2.changelog.data, company_id=company.id, department_id=department.id, document_name_id=document.id, document_section_id=section.id, submitted_by=current_user.id)
		if section_body is None:
			db.session.add(body)
			db.session.commit()
		else:
			section_body.section_body = form2.body.data
			db.session.commit()
		return redirect(url_for('documents', company_name=company.company_name, department_name=department.department_name, document_no=document.document_no, document_name=document.document_name))
	elif request.method == 'GET':
		for sect in section.body:
			form2.body.data = sect.section_body 
	return render_template('documentation_page/lab_document.html', user=user, superuser=superuser, company=company, is_super_admin=is_super_admin, is_my_affiliate=is_my_affiliate, department=department, document=document, section=section, form2=form2)	
	
@app.route('/<company_name>/<department_name>/<document_no>/<document_name>/delete_document_section/<section_id>', methods=['GET', 'POST'])
@login_required
def delete_document_section(company_name, department_name, document_no, document_name, section_id):
	company = Company.query.filter_by(company_name=company_name).first_or_404()
	department = DocumentationDepartment.query.filter_by(company_id=company.id, department_name=department_name).first()
	document = DocumentName.query.filter_by(company_id=company.id, document_no=document_no, document_name=document_name).first()
	section_id = DocumentSection.query.get(section_id)
	db.session.delete(section_id)
	db.session.commit()
	return redirect(url_for('documents', company_name=company.company_name, department_name=department.department_name, document_no=document.document_no, document_name=document.document_name))
	
@app.route('/stream', methods=['GET', 'POST'])
@login_required
def stream():
	return render_template('stream.html', user=user, superuser=superuser)
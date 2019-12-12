import os
basedir = os.path.abspath(os.path.dirname(__file__) )

class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
	SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://labApp:labApp123@localhost:3306/labApp'#os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	MAIL_SERVER = os.environ.get('MAIL_SERVER')
	MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
	MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	ADMINS = ['support@labapp.tech']
	POSTS_PER_PAGE = 25
	LANGUAGES = ['en', 'es']
	ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
	CORS_HEADERS = 'Content-Type'
	UPLOADED_PHOTOS_DEST = os.getcwd() + '/app/static/uploads/company'
	STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
	STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
	INV_SUP_SUBSCRIPTION_PLAN_ID = os.environ.get('INV_SUP_SUBSCRIPTION_PLAN_ID')
	DOMAIN = os.environ.get('DOMAIN')
	
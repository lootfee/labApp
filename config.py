import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__) )
load_dotenv()

class Config(object):
	SECRET_KEY = os.getenv('SECRET_KEY') or 'you-will-never-guess'
	SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	MAIL_SERVER = os.getenv('MAIL_SERVER')
	MAIL_PORT = int(os.getenv('MAIL_PORT') or 25)
	MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') is not None
	MAIL_USERNAME = os.getenv('MAIL_USERNAME')
	MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
	ADMINS = ['support@labapp.tech']
	POSTS_PER_PAGE = 25
	LANGUAGES = ['en', 'es']
	ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
	CORS_HEADERS = 'Content-Type'
	UPLOADED_PHOTOS_DEST = os.getcwd() + '/app/static/uploads/company'
	STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
	STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY')
	INV_SUP_SUBSCRIPTION_PLAN_ID = os.getenv('INV_SUP_SUBSCRIPTION_PLAN_ID')
	DOMAIN = os.getenv('DOMAIN')
	
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from urllib.request import Request, urlopen, URLError
from urllib.parse import urlparse
from flask_oauth import OAuth
from decouple import config as conf


app = Flask(__name__)
app.config['SECRET_KEY'] = conf('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = conf('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = conf('MAIL_PASSWORD')
mail = Mail(app)



GOOGLE_CLIENT_ID = conf('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = conf('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = '/oauth2callback'  # one of the Redirect URIs from Google APIs console
oauth = OAuth()

google = oauth.remote_app('google',
base_url='https://www.google.com/accounts/',
authorize_url='https://accounts.google.com/o/oauth2/auth',
request_token_url=None,
request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email','response_type': 'code'},
access_token_url='https://accounts.google.com/o/oauth2/token',
access_token_method='POST',
access_token_params={'grant_type': 'authorization_code'},
consumer_key=GOOGLE_CLIENT_ID,
consumer_secret=GOOGLE_CLIENT_SECRET)

class userType:
    def __init__(self,type=None):
        self._type = type
    
    def get_type(self):
        return self._type
    
    def setTypeToTeacher(self):
        self._type = "teacher"
    
    def setTypeToStudent(self):
        self._type = "student"
    
    def isStudent(self):
        if self._type == "student":
            return True
        return False
    
    def isTeacher(self):
        if self._type == "teacher":
            return True
        return False

currentUserType = userType()
from flask_app import routes

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

login = LoginManager(app)
login.login_view = 'login'

db = SQLAlchemy(app)

from app.models import User, Post
from app import routes

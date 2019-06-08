from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_mail import Mail

import os
app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database/database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
SECRET_KEY = os.environ.get('SECRET',os.urandom(32))
app.config['SECRET_KEY'] = SECRET_KEY

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'iisg.vmmanager@gmail.com'
app.config['MAIL_PASSWORD'] = "Alamakota123"
mail = Mail(app)


login_manager=LoginManager()
login_manager.session_protection="strong"
login_manager.init_app(app)

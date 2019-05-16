from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
import os
app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database/database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY



login_manager=LoginManager()
login_manager.session_protection="strong"
login_manager.init_app(app)
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app,resources={r"/*": {"origins": "*"}})

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database/database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



from flask import jsonify, request, redirect

from database.dbmodel import *
from parser.csvparser import Parser
from settings import app
import datetime
import jwt
app.config['SECRET_KEY'] ='meow'


@app.route("/login", method=['POST'])
def get_token():
    request_data = request.get_json()
    username = str(request_data['username'])
    password = str(request_data['password'])

    match = User.username_password_match(username, password)

    if match:
        expiration_date = datetime.datetime.utcnow() + datetime.timedelta(seconds=100)
        token = jwt.encode({'exp': expiration_date}, app.config['SECRET_KEY'], algorithm='HS256')
        return token
    else:
        return jsonify({'error': 'Not valid token'}), 401



@app.route("/")
def hello_world():
    return "Hello World!"


@app.route("/pools", methods=["GET"])
def get_pools():
    token=request.args.get('token')
    try:
        jwt.decode(token, app.config['SECRET_KEY'])
    except:
        return jsonify({'error': 'Not valid token'}), 401

    return jsonify({"pools": Pool.get_pools()})


@app.route("/import", methods=["POST"])
def import_pools():
    # print(request.files)
    if "pools_csv" not in request.files:
        return redirect(request.url)
    file = request.files["pools_csv"]
    parser = Parser(file)
    parser.parse_file()
    return "Received pools\n"


if __name__ == "__main__":
    app.run()

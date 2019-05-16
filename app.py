from flask import jsonify, request, redirect
import os
from database.dbmodel import Pool, db, User
from parser.csvparser import Parser
from settings import app
from sqlalchemy import  exc as sa_exc
import jwt
import datetime
import response
from functools import wraps



def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.args.get('token')
        try:
            jwt.decode(token, app.config['SECRET_KEY'])
            return f(*args, **kwargs)
        except:
            return jsonify({'error': 'not logged'}), 401
    return wrapper


@app.route("/home")
def hello_world():
        return "Hello World!"


@app.route("/")
def world():
        return "W!"

# @app.route("/test")
# @login_required
# def world():
#     return "authentykacja!"



@app.route("/login", methods=["GET", "POST"])
def get_token():

    data= request.get_json(force = True)
    email = str(data['email'])
    password = str(data['password'])

    match = User.username_password_mathc(email, password)

    if match:
        expiration_date = datetime.datetime.utcnow()+datetime.timedelta(seconds=100)
        token = jwt.encode({'exp': expiration_date}, app.config['SECRET_KEY'], algorithm='HS256')
        return token

    else:
        response('', 401, mimetype='application/json')


@app.route("/s", methods=["GET", "POST"])
def register():

    data= request.get_json(force = True)
    firstname = data['firstname']
    lastname = data['lastname']
    email = data['email']
    password = data['password']
    try:
        User.add_user(email, password, firstname, lastname)
    except sa_exc.IntegrityError:
        print("User with email: '" + email + "' already exists")

    result ={
        'firsr': firstname,
        'last': lastname,
        'email': email,
        'password': password
    }

    # test = {'test': test}
    return jsonify({'test': result})



@app.route("/pools", methods=["GET"])
@login_required
def get_pools():
    return jsonify({"pools": Pool.get_table()})


@app.route("/import", methods=["POST"])
def import_pools():
    if "pools_csv" not in request.files or "force" not in request.args:
        return redirect(request.url)

    file = request.files["pools_csv"]
    force = request.args.get("force")

    parser = Parser(file)
    parser.clear_error_list()

    if force == "true":
        parser.parse_file(True)
    else:
        parser.parse_file(False)

    if parser.is_list_empty():
        return "No errors"
    else:
        error_list = parser.get_error_list()
        return jsonify(error_list), 422



@app.route("/init_db")
@login_required
def init_db():
    # Test method for clearing and creating new empty database
    # Also can create database.db from scratch
    db.drop_all()
    db.session.commit()
    db.create_all()
    db.session.commit()
    return "Database reseted"


if __name__ == "__main__":
    app.run(debug=True)
    app.secret_key = os.urandom(12)
    app.run(debug=True, host='0.0.0.0', port=4000)
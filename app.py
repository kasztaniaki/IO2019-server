import jwt
import os
import types
import datetime

from functools import wraps
from sqlalchemy import exc as sa_exc
from flask import jsonify, request, redirect, Response

import database.mock_db as mock_db
from settings import app
from parser.csvparser import Parser
from database.dbmodel import Pool, db, Software, OperatingSystem, User, SoftwareList, Reservation


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers['Auth-Token']
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithm='HS256')
            return f(*args, **kwargs)
        except Exception as e:
            print(e)
            return jsonify({'error': 'not logged'}), 401

    return wrapper


@app.route("/")
def world():
    return "W!"


@app.route("/users/signin", methods=["GET", "POST"])
def get_token():
    data = request.get_json(force=True)
    email = str(data['email'])
    password = str(data['password'])

    match = User.username_password_match(email, password)

    if match:
        expiration_date = datetime.datetime.utcnow() + datetime.timedelta(hours=5)
        user = User.get_user_by_email(email)
        token = jwt.encode({'exp': expiration_date, 'email': user.Email},
                           app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'UserData': User.json(user), 'Token': token.decode('utf-8')})

    else:
        Response('Invalid credentials provided', 401, mimetype='application/json')


@app.route("/users/signup", methods=["GET", "POST"])
def register():
    data = request.get_json(force=True)
    firstname = data['firstname']
    lastname = data['lastname']
    email = data['email']
    password = data['password']
    try:
        User.add_user(email, password, firstname, lastname)
    except sa_exc.IntegrityError:
        print("User with email: '" + email + "' already exists")

    result = {
        'first': firstname,
        'last': lastname,
        'email': email,
        'password': password
    }

    return jsonify({'test': result})


@app.route("/users/edit_user", methods=["POST"])
@login_required
def edit_user():
    if "email" not in request.args:
        return "User ID not provided in request", 400
    if not request.json:
        return "User data not provided", 400

    email = request.args.get('email')
    try:
        user = User.get_user_by_email(email)
        user.set_name(request.json.get('new_name', user.Name))
        user.set_surname(request.json.get('new_surname', user.Surname))
        user.set_password(request.json.get('new_password', user.Password))

        logged_user_email = jwt.decode(request.headers['Auth-Token'], app.config['SECRET_KEY'],
                                       algorithm='HS256')['email']
        if User.get_user_by_email(logged_user_email).IsAdmin:
            user.set_email(request.json.get('new_email', user.Email))
            user.set_admin_permissions(request.json.get('is_admin', user.IsAdmin))
        return "User successfully edited", 200
    except ValueError:
        return "User of given e-mail already exists", 422
    except AttributeError as e:
        print(e)
        return "User of ID {} doesn't exist".format(id), 404


@app.route("/users/remove_user", methods=["POST"])
@login_required
def remove_user():
    if "email" not in request.args:
        return "User ID not provided in request", 400
    user_email = request.args.get('email')
    try:
        user = User.get_user_by_email(user_email)
        user.remove()
    except Exception as e:
        print(e)
        return "User with email: {} doesn't exist!".format(id), 404
    return "User with email: {} successfully deleted".format(id), 200


@app.route("/pools", methods=["GET"])
@login_required
def get_pools():
    return jsonify({"pools": Pool.get_table()})


@app.route("/users", methods=["GET"])
@login_required
def get_users():
    return jsonify({"users": User.get_table()})


@app.route("/user", methods=["GET"])
@login_required
def get_user():
    if "email" not in request.args:
        return "User email not provided in request", 400
    email = request.args.get('email')
    try:
        user = User.get_user_by_email(email)
        return jsonify({"user": User.json(user)})
    except AttributeError:
        return "User of email '{}' doesn't exist".format(email), 404


@app.route("/pool", methods=["GET"])
@login_required
def get_pool():
    if "id" not in request.args:
        return "Pool ID not provided in request", 400
    pool_id = request.args.get('id')
    try:
        pool = Pool.get_pool(pool_id)
        return jsonify({"pool": Pool.json(pool)})
    except AttributeError:
        return "Pool of ID {} doesn't exist".format(pool_id), 404


@app.route("/add_pool", methods=["POST"])
@login_required
def add_pool():
    if not request.json:
        return "Pool data not provided", 400
    try:
        pool_id = request.json['ID']
        pool = Pool.add_pool(pool_id,
                             request.json['Name'],
                             request.json.get('MaximumCount', 0),
                             request.json.get('Description', ''),
                             request.json.get('Enabled', False)
                             )
        operating_system = request.json.get('OSName', '')
        if operating_system:
            operating_system = OperatingSystem.add_operating_system(operating_system)
            pool.set_operating_system(operating_system)

        installed_software = request.json.get('InstalledSoftware', [])
        for name, version in installed_software:
            software = Software.add_software(name)
            pool.add_software(software, version)
        return Pool.get_pool(pool_id).ID, 200
    except KeyError as e:
        return "Value of {} missing in given JSON".format(e), 400
    except ValueError:
        return "Pool of given ID already exists", 422


@app.route("/edit_pool", methods=["POST"])
@login_required
def edit_pool():
    if "id" not in request.args:
        return "Pool ID not provided in request", 400
    if not request.json:
        return "Pool data not provided", 400

    pool_id = request.args.get('id')
    try:
        pool = Pool.edit_pool(pool_id,
                              request.json['ID'],
                              request.json['Name'],
                              request.json.get('MaximumCount', ''),
                              request.json.get('Description', ''),
                              request.json.get('Enabled', False)
                              )
        pool.edit_software(request.json.get('InstalledSoftware', []))

        operating_system = request.json.get('OSName', '')
        if operating_system:
            operating_system = OperatingSystem.add_operating_system(operating_system)
            pool.set_operating_system(operating_system)

        return "Pool successfully edited", 200
    except ValueError:
        return "Pool of given ID already exists", 422
    except AttributeError as e:
        print(e)
        return "Pool of ID {} doesn't exist".format(pool_id), 404


@app.route("/remove_pool", methods=["GET"])
@login_required
def remove_pool():
    if "id" not in request.args:
        return "Pool ID not provided in request", 400
    pool_id = request.args.get('id')
    try:
        pool = Pool.get_pool(pool_id)
        pool.remove()
    except Exception as e:
        print(e)
        return "Pool of ID {} doesn't exist!".format(id), 404
    return "Pool of ID {} successfully deleted".format(id), 200


@app.route("/import", methods=["POST"])
@login_required
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

    if parser.is_list_empty() or force == "true":
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
    User.add_user("admin@admin.example", "ala123456", "Admin", "Admin", True)
    db.session.commit()
    if bool(int(os.environ.get('MOCK', 0))):
        mock_db.gen_mock_data()
    return "Database reseted"


@app.before_first_request
def initialize():
    # tricky, but omits the login_required decorator at startup
    list(filter(lambda val: isinstance(val, types.FunctionType) and val.__name__ == "init_db",
                init_db.__dict__.values()))[0]()


if __name__ == "__main__":
    app.run(debug=True)

from flask import jsonify, request, redirect
from database.dbmodel import Pool, db, Software, OperatingSystem, User, SoftwareList
from parser.csvparser import Parser
from settings import app


@app.route("/")
def hello_world():
    return "Hello World!"


@app.route("/pools", methods=["GET"])
def get_pools():
    return jsonify({"pools": Pool.get_table()})


@app.route("/pool", methods=["GET"])
def get_pool():
    if "id" not in request.args:
        return "Pool ID not provided in request", 400
    id = request.args.get('id')
    try:
        pool = Pool.get_pool(id)
        return jsonify({"pool": Pool.json(pool)})
    except AttributeError:
        return "Pool of ID {} doesn't exist".format(id), 404


@app.route("/add_pool", methods=["POST"])
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
        os = request.json.get('OSName', '')
        if os:
            operating_system = OperatingSystem.add_operating_system(os)
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
def edit_pool():
    if "id" not in request.args:
        return "Pool ID not provided in request", 400
    if not request.json:
        return "Pool data not provided", 400

    id = request.args.get('id')
    try:
        pool = Pool.edit_pool(id,
                              request.json['ID'],
                              request.json['Name'],
                              request.json.get('MaximumCount', ''),
                              request.json.get('Description', ''),
                              request.json.get('Enabled', False)
                              )
        pool.edit_software(request.json.get('InstalledSoftware', []))

        os = request.json.get('OSName', '')
        if os:
            operating_system = OperatingSystem.add_operating_system(os)
            pool.set_operating_system(operating_system)

        return "Pool successfully edited", 200
    except ValueError:
        return "Pool of given ID already exists", 422
    except AttributeError as e:
        print(e)
        return "Pool of ID {} doesn't exist".format(id), 404


@app.route("/remove_pool", methods=["GET"])
def remove_pool():
    if "id" not in request.args:
        return "Pool ID not provided in request", 400
    try:
        id = request.args.get('id')
        Pool.remove_pool(id)
    except Exception as e:
        print(e)
        return "Pool of ID {} doesn't exist!".format(id), 404
    return "Pool of ID {} successfully deleted".format(id), 200


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
def init_db():
    # Test method for clearing and creating new empty database
    # Also can create database.db from scratch
    db.drop_all()
    db.session.commit()
    db.create_all()
    db.session.commit()
    return "Database reseted"


@app.route("/account", methods=["GET"])
def manage_user_profile():
    if "id" not in request.args:
        return "User ID not provided in request", 400
    id = request.args.get('id')
    try:
        user = User.get_user(id)
        return jsonify({"user": User.json(user)})
    except AttributeError:
        return "User of ID {} doesn't exist".format(id), 404


@app.route("/accounts", methods=["GET"])
def manage_profiles():
    return jsonify({"users": User.get_table()})


@app.route("/delete_account", methods=["GET"])
def delete_user_profile():
    if "id" not in request.args:
        return "User ID not provided in request", 400
    id = request.args.get('id')
    try:
        User.remove_user(id)
        return "User of ID {} is deleted".format(id)
    except AttributeError:
        return "User of ID {} doesn't exist".format(id), 404


@app.route("/add_account", methods=["POST"])
def add_account():
    if not request.json:
        return "Account data not provided", 400
    try:
        user_id = request.json['ID']
        user = User.add_user(request.json['Email'],
                             request.json['Password'],
                             request.json['Name'],
                             request.json['Surname'],
                             request.json.get('IsAdmin', '')
                             )
        return User.get_user(user_id).ID, 200
    except KeyError as e:
        return "Value of {} missing in given JSON".format(e), 400
    except ValueError:
        return "User of given ID already exists", 422


@app.route("/edit_user", methods=["POST"])
def edit_user():
    if "id" not in request.args:
        return "User ID not provided in request", 400
    if not request.json:
        return "User data not provided", 400

    id = request.args.get('id')
    try:
        user = User.edit_user(id,
                              request.json['Email'],
                              request.json['Password'],
                              request.json.get('Name'),
                              request.json.get('Surname'),
                              request.json.get('IsAdmin', '')
                              )

        return "User successfully edited", 200
    except ValueError:
        return "User of given ID already exists", 422
    except AttributeError as e:
        print(e)
        return "User of ID {} doesn't exist".format(id), 404


if __name__ == "__main__":
    app.run()

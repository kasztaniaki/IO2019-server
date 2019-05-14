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
        return "Invalid request", 422
    id = request.args.get('id')
    try:
        pool = Pool.get_pool(id)
        return jsonify({"pool": Pool.json(pool)})
    except AttributeError:
        return "Pool of ID {} doesn't exist!".format(id), 404


@app.route("/add_pool", methods=["POST"])
def add_pool():
    if not request.json:
        return "Invalid request", 422
    try:
        pool_id = request.json['ID']
        pool = Pool.add_pool(pool_id,
                             request.json['Name'],
                             request.json.get('MaximumCount', 0),
                             request.json.get('Description', ''),
                             request.json.get('Enabled', False))
        installed_software = request.json.get('InstalledSoftware', [])
        for name, version in installed_software:
            sw = Software.add_software(name)
            pool.add_software(sw, version)
        return Pool.get_pool(pool_id).ID
    except KeyError as e:
        return "Value of {} missing in given JSON".format(e)


@app.route("/edit_pool", methods=["POST"])
def edit_pool():
    if "id" not in request.args or not request.json:
        return "Invalid request", 422
    id = request.args.get('id')

    try:
        pool = Pool.get_pool(id)
        installed_software = request.json.get('InstalledSoftware', [])
        sw_to_remove = list(filter(lambda x: list(x[1:]) not in installed_software,
                                   pool.get_software_list()))

        for sw in sw_to_remove:
            pool.remove_software(sw[0], sw[1])

        sw_to_add = list(filter(lambda x: x not in [list(y[1:])
                                                    for y in pool.get_software_list()],
                                installed_software))

        for name, version in sw_to_add:
            sw = Software.add_software(name)
            pool.add_software(sw, version)

        Pool.edit_pool(id,
                       request.json['ID'],
                       request.json['Name'],
                       request.json.get('MaximumCount', ''),
                       request.json.get('Description', ''),
                       request.json.get('Enabled', False))
        return Pool.get_pool(request.json['ID']).ID
    except AttributeError as e:
        print(e)
        return "Pool of ID {} doesn't exist!".format(id), 404


@app.route("/rm_pool", methods=["GET"])
def rm_pool():
    if "id" not in request.args:
        return "Invalid request", 422
    id = request.args.get('id')
    try:
        Pool.rm_pool(id)
        return str(not Pool.get_pool(id))
    except AttributeError as e:
        return "Pool of ID {} doesn't exist!".format(id), 404


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


if __name__ == "__main__":
    app.run()

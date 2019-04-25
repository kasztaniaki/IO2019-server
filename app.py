from flask import jsonify, request, redirect

from database.dbmodel import Pool
from parser.csvparser import Parser
from settings import app


@app.route("/")
def hello_world():
    return "Hello World!"


@app.route("/pools", methods=["GET"])
def get_pools():
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

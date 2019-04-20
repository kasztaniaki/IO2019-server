from flask import Flask, jsonify

from database.dbmodel import Pool
from settings import app


@app.route("/")
def hello_world():
    return "Hello World!"


@app.route('/pools', methods=['GET'])
def get_pools():
    return jsonify({'pools': Pool.get_pools()})


if __name__ == "__main__":
    app.run()

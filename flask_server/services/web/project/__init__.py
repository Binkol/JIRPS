from flask import Flask, jsonify
from project.models import db


app = Flask(__name__)
app.config.from_object("project.config.Config")

db.init_app(app)


@app.route("/")
def hello_world():
    return jsonify(hello="world")
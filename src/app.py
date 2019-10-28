from flask import Flask, render_template
from utility import *
from flask_mysqldb import MySQL

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", title="Index")


@app.route("/forms/create")
def create_form():
    return "Create a form here"


@app.route("/forms/")
@app.route("/forms/index")
def view_forms():
    return render_template("survey/index.html", title="Survey Home")


@app.route("/forms/view")
def view_form():
    return render_template("survey/view.html", title="Survey Detail")


if __name__ == "__main__":
    info = load_database_info()
    if info is None:
        exit(1)
    app.secret_key = info['secret_key']
    app.config['MYSQL_HOST'] = info['host']
    app.config['MYSQL_USER'] = info['user']
    app.config['MYSQL_PASSWORD'] = info['password']
    app.config['MYSQL_DB'] = info['db']
    app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

    mysql = MySQL(app)
    app.run(debug=True)

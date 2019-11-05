from flask import Flask, render_template, request, session
from utility import *
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", title="Index")


@app.route("/login", methods=["GET", "POST"])
def login():

    HAVE_NOT_FIXED_DATABASE_YET = True

    if request.method == "POST" and not HAVE_NOT_FIXED_DATABASE_YET:
        username = request.form["username"]
        pass_candidate = request.form["password"]
        cur = mysql.connection.cursor()
        res = cur.execute("SELECT * FROM users WHERE username=%s", [username])
        cur.close()
        if res > 0:
            user = cur.fetchone()
            password = user['password']

            if sha256_crypt.verify(pass_candidate, password):
                session['logged_in'] = True
                session['username'] = user['username']
            else:
                error = "Invalid User or Password"
                return render_template("login.html", error=error)
        else:
            error = "Invalid User or Password"
            return render_template("login.html", error=error)
    else:
        return render_template("login.html")


@app.route("/forms/")
@app.route("/forms/index")
def view_forms():
    return render_template("survey/index.html", title="Survey Home")


@app.route("/forms/new")
def create_form():
    return render_template("survey/new.html", title="Create New Survey")


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

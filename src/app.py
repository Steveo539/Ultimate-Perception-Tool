from flask import Flask, render_template, request, session, redirect, url_for
from utility import *
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from access import *

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", title="Index")

# Table sql line: CREATE TABLE users(id INT(12) AUTO_INCREMENT PRIMARY KEY, username VARCHAR(30), password VARCHAR(100))
# Creates a test user with username: manager and password: test
@app.route("/gen_user")
def create_user():
    cur = mysql.connection.cursor()
    res = cur.execute("SELECT * FROM users WHERE username=%s", ["manager"])
    if res > 0:
        cur.close()
        return "Already created user"
    else:
        username = "manager"
        password = sha256_crypt.encrypt("test")
        cur.execute("INSERT INTO users(username, password) VALUES(%s, %s)", (username, password))
        mysql.connection.commit()
        cur.close()
        return "Created user"


@app.route("/login", methods=["GET", "POST"])
@is_logged_out
def login():
    if request.method == "POST":
        username = request.form["username"]
        pass_candidate = request.form["password"]
        cur = mysql.connection.cursor()
        res = cur.execute("SELECT * FROM users WHERE username=%s", [username])
        if res > 0:
            user = cur.fetchone()
            cur.close()
            password = user['password']

            if sha256_crypt.verify(pass_candidate, password):
                session['logged_in'] = True
                session['username'] = user['username']
                return redirect(url_for("index"))
            else:
                error = "Invalid User or Password"
                return render_template("login.html", error=error)
        else:
            cur.close()
            error = "Invalid User or Password"
            return render_template("login.html", error=error)
    else:
        return render_template("login.html")


@app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/forms/")
@app.route("/forms/index")
@is_logged_in
def view_forms():
    return render_template("survey/index.html", title="Survey Home")


@app.route("/forms/new")
@is_logged_in
def create_form():
    return render_template("survey/new.html", title="Create New Survey")


@app.route("/forms/view")
@is_logged_in
def view_form():
    return render_template("survey/view.html", title="Survey Detail")


@app.before_first_request
def create_tables():
    cur = mysql.connection.cursor()
    res = cur.execute("SHOW TABLES LIKE \'users\'")
    if res < 1:
        print("Creating user table...")
        cur.execute("CREATE TABLE users(id INT(12) AUTO_INCREMENT PRIMARY KEY, username VARCHAR(30), password VARCHAR(100))")
        mysql.connection.commit()
    cur.close()

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

from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
from passlib.handlers.sha2_crypt import sha256_crypt

from src.access import is_logged_in, is_logged_out
from src.database_functions import get_questions, add_question
from src.form_functions import build_form
from src.utility import load_database_info

app = Flask(__name__, static_url_path='', static_folder='static/', template_folder='templates/')


@app.route("/")
def index():
    return render_template("index.html")


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


@app.route("/gen_form")
def gen_form():
    cur = mysql.connection.cursor()
    res = cur.execute("SHOW TABLES LIKE \'form_1\'")
    if res < 1:
        print("Creating test form table...")
        cur.execute(
            "CREATE TABLE form_1(id INT(12) AUTO_INCREMENT PRIMARY KEY, type VARCHAR(25), text VARCHAR(100), options VARCHAR(200))")
        mysql.connection.commit()

    question_1 = {"text": "What is your favorite color?", "type": "string", "options": ""}
    question_2 = {"text": "What is your favorite letter?", "type": "radio",
                  "options": [("a", "a"), ("b", "b"), ("c", "c"), ("d", "d")]}
    question_3 = {"text": "What is the magic word?", "type": "string", "options": ""}
    add_question(mysql, 1, question_1)
    add_question(mysql, 1, question_2)
    add_question(mysql, 1, question_3)
    cur.close()
    return "Added questions"


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
                session['user_id'] = user['id']
                return redirect(url_for("index"))
            else:
                error = "Invalid User or Password"
                return render_template("authentication/login.html", error=error)
        else:
            cur.close()
            error = "Invalid User or Password"
            return render_template("authentication/login.html", error=error)
    else:
        return render_template("authentication/login.html")


@app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/forms/")
@is_logged_in
def view_library():
    cur = mysql.connection.cursor()
    manager_id = session['user_id']
    result = cur.execute("SELECT name,id FROM surveys WHERE employee_id=%s", [str(manager_id)])
    manager_surveys = {}
    if result > 0:
        manager_surveys = cur.fetchmany()
    return render_template("survey/index.html", title="Survey Home", surveys=manager_surveys)


@app.route("/forms/new", methods=["GET", "POST"])
@is_logged_in
def create_form():
    return render_template("survey/new.html", title="Create New Survey")


@app.route("/forms/view/<form_id>")
@is_logged_in
def view_form(form_id):
    questions = get_questions(mysql, form_id)
    if len(questions) < 1:
        return "Invalid Form ID"
    form = build_form(questions)
    return render_template("survey/view.html", title="Survey Detail", form=form)


@app.before_first_request
def create_tables():
    cur = mysql.connection.cursor()
    res = cur.execute("SHOW TABLES LIKE \'users\'")
    if res < 1:
        print("Creating user table...")
        cur.execute(
            "CREATE TABLE users(id INT(12) AUTO_INCREMENT PRIMARY KEY, username VARCHAR(30), password VARCHAR(100))")
        mysql.connection.commit()
        res = cur.execute("SHOW TABLES LIKE \'users\'")
    if res < 1:
        print("Creating survey table...")
        cur.execute(
            "CREATE TABLE surveys(id INT(12) AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), employee_id INT(12) REFERENCES users(id), company_id INT(12))")
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

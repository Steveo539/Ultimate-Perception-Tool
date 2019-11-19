from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
from passlib.handlers.sha2_crypt import sha256_crypt
from datetime import datetime

from src.access import is_logged_in, is_logged_out
from src.database_functions import get_questions, add_question
from src.form_functions import build_form
from src.utility import load_database_info, check_unique_user
from src.forms import RegisterForm

app = Flask(__name__, static_url_path='', static_folder='static/', template_folder='templates/')


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/gen_user")
@is_logged_out
def gen_user():
    cur = mysql.connection.cursor()
    res = cur.execute("SELECT * FROM users WHERE username=%s", ["manager"])
    if res > 0:
        cur.close()
        return "Account already exists, login with username: manager and password: test1"
    else:
        password = sha256_crypt.encrypt("test1")
        cur.execute("INSERT INTO users(name, username, password, positionTitle, email, startDate) VALUES(%s, %s, %s, %s, %s, %s)", ("manager", "manager", password, "Manager", "manager@email.com", "1/1/1970"))
        mysql.connection.commit()
        cur.close()
        return "Account Created with username: manager and password: test1"


@app.route("/gen_form")
def gen_form():
    cur = mysql.connection.cursor()
    res = cur.execute("SHOW TABLES LIKE \'form_1\'")
    if res < 1:
        print("Creating test form table...")
        cur.execute("CREATE TABLE form_1(id INT(12) AUTO_INCREMENT PRIMARY KEY, type VARCHAR(25), text VARCHAR(100), options VARCHAR(200))")
        mysql.connection.commit()

    question_1 = {"text": "What is your favorite color?", "type": "string", "options": ""}
    question_2 = {"text": "What is your favorite letter?", "type": "radio", "options": [("a","a"),("b","b"),("c","c"),("d","d")]}
    question_3 = {"text": "What is the magic word?", "type": "string", "options": ""}
    add_question(mysql, 1, question_1)
    add_question(mysql, 1, question_2)
    add_question(mysql, 1, question_3)
    cur.close()
    return "Added questions"


@app.route("/register", methods=["GET", "POST"])
@is_logged_out
def register():
    form = RegisterForm()
    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        position = form.position.data
        password = sha256_crypt.encrypt(str(form.password.data))
        company = form.company.data
        date_started = datetime.now().strftime("%m/%d/%Y")

        if check_unique_user(username, email, mysql):
            return render_template("authentication/register.html", form=form)

        cur = mysql.connection.cursor()

        res = cur.execute("SELECT * FROM companies WHERE companyID=%s", [company])
        if res < 1:
            return render_template("authentication/register.html", form=form)

        cur.execute("INSERT INTO users(companyID, name, username, password, positionTitle, email, startDate) VALUES(%s, %s, %s, %s, %s, %s, %s)", (company, name, username, password, position, email, date_started))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("index"))

    return render_template("authentication/register.html", form=form)


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
@app.route("/forms/index")
@is_logged_in
def view_forms():
    return render_template("survey/index.html", title="Survey Home")


@app.route("/forms/new", methods=["GET", "POST"])
@is_logged_in
def create_form():
    return render_template("survey/new.html", title="Create New Survey")


@app.route("/forms/view")
@is_logged_in
def view_form():
    questions = get_questions(mysql, 1)
    form = build_form(questions)
    return render_template("survey/view.html", title="Survey Detail", form=form)


@app.before_first_request
def create_tables():
    cur = mysql.connection.cursor()
    res = cur.execute("SHOW TABLES LIKE \'companies\'")
    if res < 1:
        print("Creating company table...")
        cur.execute("CREATE TABLE companies(companyID INT(12) PRIMARY KEY, companyName VARCHAR(100))")
        mysql.connection.commit()
    res = cur.execute("SHOW TABLES LIKE \'users\'")
    if res < 1:
        print("Creating user table...")
        cur.execute("CREATE TABLE users(companyID INT(18), ID INT(18) AUTO_INCREMENT PRIMARY KEY, name VARCHAR(150), username VARCHAR(30), password VARCHAR(100), positionTitle VARCHAR(100), email VARCHAR(100), startDate VARCHAR(20), FOREIGN KEY (companyID) REFERENCES companies(companyID))")
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

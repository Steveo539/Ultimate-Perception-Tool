from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
from passlib.handlers.sha2_crypt import sha256_crypt
from datetime import datetime

from src.access import is_logged_in, is_logged_out
from src.database_functions import get_questions, create_admin, get_companies, delete_company, add_company
from src.form_functions import build_form
from src.utility import load_database_info, check_unique_user, create_tables
from src.forms import RegisterForm

app = Flask(__name__, static_url_path='', static_folder='static/', template_folder='templates/')


@app.route("/")
def index():
    return render_template("index.html")


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
            return render_template("authentication/register.html", form=form, title="Register")

        cur = mysql.connection.cursor()

        res = cur.execute("SELECT * FROM companies WHERE companyID=%s", [company])
        if res < 1:
            return render_template("authentication/register.html", form=form, title="Register")

        cur.execute("INSERT INTO users(companyID, name, username, password, positionTitle, email, startDate) VALUES(%s, %s, %s, %s, %s, %s, %s)", (company, name, username, password, position, email, date_started))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("index"))

    return render_template("authentication/register.html", form=form, title="Register")


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
                session['user_id'] = user['ID']
                return redirect(url_for("index"))
            else:
                error = "Invalid User or Password"
                return render_template("authentication/login.html", error=error, title="Sign In")
        else:
            cur.close()
            error = "Invalid User or Password"
            return render_template("authentication/login.html", error=error, title="Sign In")
    else:
        return render_template("authentication/login.html", title="Sign In")


@app.route("/logout")
@is_logged_in
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/manage/companies", methods=["GET", "POST"])
@is_logged_in
def manage_companies():
    if session['username'] != "admin":
        return redirect(url_for("index"))

    if request.method == "POST":
        if "delete_company" in request.form:
            company = request.form["delete_company"]
            delete_company(mysql, company)
        elif "add_company" in request.form:
            company = request.form["company_name"]
            if len(company) > 2:
                add_company(mysql, company)

    return render_template("management/companies.html", title="Manage Companies", companies=get_companies(mysql))


@app.route("/forms/")
@is_logged_in
def view_library():
    cur = mysql.connection.cursor()
    manager_id = session['user_id']
    result = cur.execute("SELECT surveyName, ID FROM surveys WHERE userID=%s", [str(manager_id)])
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
def handle_setup():
    create_tables(mysql)
    create_admin(mysql)


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

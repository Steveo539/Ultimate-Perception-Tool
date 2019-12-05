from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
from passlib.handlers.sha2_crypt import sha256_crypt
from datetime import datetime

from src.access import is_logged_in, is_logged_out

from src.database_functions import *
from src.emails import email_user, notify_users

from src.form_functions import build_form
from src.utility import load_database_info, check_unique_user, create_tables, load_email_info
from src.forms import RegisterForm

app = Flask(__name__, static_url_path='', static_folder='static/', template_folder='templates/')


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/test_survey")
def test_survey():

    cur = mysql.connection.cursor()
    res = cur.execute("SELECT * FROM surveys WHERE ID=%s", [str(1)])
    if res > 0:
        cur.close()
        return "Already created survey"
    cur.close()

    survey = {"name": "Test 1", "user": "1", "date": "1/14/1970"}
    create_survey(mysql, survey)
    question1 = {'text': "What is your favorite color?", 'type': "string", 'options': ""}
    question2 = {'text': "What is your favorite number?", 'type': "integer", 'options': ""}
    question3 = {'text': "What is your favorite letter?", 'type': "radio", 'options': [("a", "a"), ("b", "b"), ("c", "c"), ("d", "d")]}
    question4 = {'text': "What is your favorite sport?", 'type': "select", 'options': [("baseball", "baseball"), ("football", "football"), ("basketball", "basketball")]}

    add_question(mysql, 1, question1)
    add_question(mysql, 1, question2)
    add_question(mysql, 1, question3)
    add_question(mysql, 1, question4)
    return "Created survey"


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


@app.route("/forms/send/", methods=["GET", "POST"])
@app.route("/forms/send/<survey_id>", methods=["GET", "POST"])
def send_survey(survey_id=-1):
    """Validates UUID from an employee. If valid will direct employee to the survey associated with the
    UUID. Otherwise, will redirect employee back to this page with an error message."""
    if not app.config['EMAIL_ENABLED']:  # If email is not enabled, then we don't notify
        return "Unable To Complete Action. Email Functionality is not Enabled."
    message = None
    error = None
    if request.method == "POST":
        survey_id = request.form['survey_id']
        recipients = request.form["recipients"]
        try:
            cur = mysql.connection.cursor()
            res = cur.execute("SELECT * FROM surveys WHERE surveyID=%s AND managerID=%s", [int(survey_id), session['user_id']])
            if res > 0:
                cur.close()
                if len(recipients) > 0:
                    notify_users(mysql, survey_id, session['user_id'], recipients)
                    message = 'Successfully Notified Employees!'
                else:
                    error = 'Please specify email recipients.'
            else:
                error = 'Please provide a valid ID to a survey that you have created.'
        except ValueError:  # Catch if user doesn't provide valid survey ID
            error = 'Please provide a valid survey ID as a number.'

    if survey_id != -1:  # If user provided a form ID in URL, autofill the form with it.
        return render_template("survey/send_survey.html", title="Send Survey", form_id=survey_id, message=message, error=error)
    return render_template("survey/send_survey.html", title="Send Survey", message=message, error=error)


@app.route("/forms/")
@is_logged_in
def view_library():
    cur = mysql.connection.cursor()
    manager_id = session['user_id']
    result = cur.execute("SELECT surveyName, surveyID FROM surveys WHERE managerID=%s", [int(manager_id)])
    manager_surveys = {}
    if result > 0:
        manager_surveys = cur.fetchmany(result)
    return render_template("survey/index.html", title="Survey Home", surveys=manager_surveys)


@app.route("/forms/validate/", methods=["GET", "POST"])
@app.route("/forms/validate/<uuid>", methods=["GET", "POST"])
def validate_uuid(uuid=-1):
    """Validates UUID from an employee. If valid will direct employee to the survey associated with the
    UUID. Otherwise, will redirect employee back to this page with an error message."""
    error = None
    if request.method == "POST":
        try:
            uuid_input = request.form["uuid_input"]
            cur = mysql.connection.cursor()
            res = cur.execute("SELECT * FROM hashes WHERE hash=%s", [int(uuid_input)])
            if res > 0:
                result = cur.fetchone()
                cur.close()
                if result['used'] != 0:  # Don't allow used hashes to be used again.
                    error = 'This access key has already been used!'
                else:
                    return redirect(url_for('view_form', form_id=result['surveyID']))
            else:
                error = 'Invalid access key.'
        except ValueError:
            error = 'Please provide a valid numeric key.'

    if uuid != -1:  # If user provided a UUID in URL, autofill the form with it.
        return render_template("survey/uuid.html", title="Validate Survey Access", uuid=uuid, error=error)
    return render_template("survey/uuid.html", title="Validate Survey Access", error=error)


@app.route("/forms/new", methods=["GET", "POST"])
@is_logged_in
def create_form():
    return render_template("survey/new.html", title="Create New Survey")


@app.route("/forms/view/<form_id>")
def view_form(form_id):
    questions = get_questions(mysql, form_id)
    form = build_form(questions)
    return render_template("survey/view.html", title="Survey Detail", form=form)


@app.before_first_request
def handle_setup():
    create_tables(mysql)
    create_admin(mysql)


@app.context_processor
def inject_stage_and_region():
    return dict(email_enabled=app.config['EMAIL_ENABLED'])


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

    # Load in email configuration from file. If not provided, app will work, but without email functionality.
    email_info = load_email_info()
    if email_info is None:
        app.config['EMAIL_ENABLED'] = False
    else:
        app.config['EMAIL_ENABLED'] = True
        app.config['EMAIL_HOST'] = email_info['host']
        app.config['EMAIL_PORT'] = email_info['port']
        app.config['EMAIL_ACCOUNT'] = email_info['account']
        app.config['EMAIL_PASSWORD'] = email_info['password']

    mysql = MySQL(app)
    app.run(debug=True)

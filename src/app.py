import json
from datetime import datetime, timedelta

from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL

from src.access import is_logged_in, is_logged_out
from src.database_functions import *
from src.emails import notify_users
from src.form_functions import build_form
from src.forms import RegisterForm
from src.utility import *

app = Flask(__name__, static_url_path='', static_folder='static/', template_folder='templates/')


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html", title="About Us")


@app.route("/test_survey")
def test_survey():
    cur = mysql.connection.cursor()
    res = cur.execute("SELECT * FROM surveys WHERE surveyID=%s", [str(1)])
    if res > 0:
        cur.close()
        return "Already created survey"
    cur.close()

    survey = {"name": "Test 1", "user": "1", "date": "1/14/1970"}
    create_survey(mysql, survey)
    question1 = {'text': "What is your favorite color?", 'type': "string", 'options': ""}
    question4 = {'text': "What is your favorite sport?", 'type': "select",
                 'options': [("baseball", "baseball"), ("football", "football"), ("basketball", "basketball")]}

    add_question(mysql, 1, question1)
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

        cur.execute(
            "INSERT INTO users(companyID, name, username, password, positionTitle, email, startDate) VALUES(%s, %s, %s, %s, %s, %s, %s)",
            (company, name, username, password, position, email, date_started))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("index"))

    return render_template("authentication/register.html", form=form, title="Register")


@app.route("/manage/user", methods=["GET", "POST"])
@is_logged_in
def user_settings():
    if request.method == "POST":
        old_password_candidate = request.form['oldpwd']
        new_password = request.form['newpwd']
        repeat_password = request.form['reppwd']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE ID=%s", [session['user_id']])
        old_password = cur.fetchone()['password']
        if sha256_crypt.verify(old_password_candidate, old_password):
            if new_password == repeat_password:
                new_password = sha256_crypt.encrypt(str(new_password))
                cur.execute("UPDATE users SET password = %s WHERE ID=%s", [new_password, session['user_id']])
                mysql.connection.commit()
                cur.close()
                return redirect(url_for("index"))
        cur.close()
    return render_template("management/user.html", title="User Settings")


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


@app.route("/forms/close/<survey_id>", methods=["GET"])
@is_logged_in
def close_survey(survey_id):
    cur = mysql.connection.cursor()
    res = cur.execute("SELECT * FROM surveys WHERE surveyID=%s AND managerID=%s",
                      [int(survey_id), session['user_id']])
    if res > 0:
        current_time = datetime.now()
        current_time = datetime.strftime(current_time, '%Y-%m-%dT%H:%M')
        res = cur.execute("UPDATE surveys SET surveyCompletionDate=%s WHERE surveyID=%s",
                          [current_time, int(survey_id)])
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("view_library"))
    else:
        return redirect(url_for("index"))


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
        recipients = request.form["recipients"]
        close_date = request.form["endDate"]
        release_date = datetime.today().strftime('%Y-%m-%dT%H:%M')
        cur = mysql.connection.cursor()
        if close_date == '':
            close_date = (datetime.today() + timedelta(days=1, minutes=1, seconds=1))
            close_date = close_date.strftime('%Y-%m-%dT%H:%M')
        else:
            close_date = datetime.strptime(close_date, '%Y-%m-%dT%H:%M')
            close_date = close_date.strftime('%Y-%m-%dT%H:%M')

        res = cur.execute("SELECT * FROM surveys WHERE surveyID=%s AND managerID=%s",
                          [int(survey_id), session['user_id']])
        if res > 0:
            cur.close()
            if len(recipients) > 0:
                notify_users(mysql, survey_id, session['user_id'], recipients)
                cur = mysql.connection.cursor()
                res = cur.execute("UPDATE surveys SET surveyCompletionDate=%s, surveyReleaseDate =%s WHERE surveyID=%s",
                                  [close_date, release_date, int(survey_id)])
                mysql.connection.commit()
                cur.close()
                return redirect(url_for("view_library"))
            else:
                error = 'Please specify email recipients.'
        else:
            error = 'Please provide a valid ID to a survey that you have created.'

    cur = mysql.connection.cursor()
    result = cur.execute("SELECT surveyName FROM surveys WHERE surveyID=%s", [int(survey_id)])
    if result > 0:
        survey_name = cur.fetchone()['surveyName']
    else:
        return redirect(url_for("view_library"))

    return render_template("survey/send_survey.html", title="Send Survey", survey_name=survey_name, message=message,
                           error=error)


@app.route("/forms/")
@is_logged_in
def view_library():
    cur = mysql.connection.cursor()
    manager_id = session['user_id']
    result = cur.execute(
        "SELECT surveyName, surveyID, surveyReleaseDate, surveyCompletionDate FROM surveys WHERE managerID=%s",
        [int(manager_id)])
    manager_surveys = {}
    if result > 0:
        manager_surveys = cur.fetchmany(result)

    today = datetime.today().strftime('%Y-%m-%d')
    for survey in manager_surveys:
        if survey['surveyReleaseDate'] is None or survey['surveyCompletionDate'] is None:
            survey['status'] = 'ready_to_send'
        elif not after_today(survey['surveyReleaseDate']) and after_today(survey['surveyCompletionDate']):
            survey['status'] = 'in_progress'
        else:
            survey['status'] = 'completed'
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
                    return redirect(url_for("validate_uuid"))
                else:
                    questions = get_questions(mysql, result['surveyID'])
                    form_name = get_form_name(mysql, result['surveyID'])
                    form = build_form(questions)
                    return render_template("survey/view.html", title="Take Survey", form=form, uuid=uuid,
                                           surveyID=result['surveyID'], name=form_name)
            else:
                error = 'Invalid access key.'
                return redirect(url_for("validate_uuid"))
        except ValueError:
            error = 'Please provide a valid numeric key.'
            return redirect(url_for("validate_uuid"))

    if uuid != -1:  # If user provided a UUID in URL, autofill the form with it.
        return render_template("survey/uuid.html", title="Validate Survey Access", uuid=uuid, error=error)
    return render_template("survey/uuid.html", title="Validate Survey Access", error=error)


@app.route("/forms/new", methods=["GET", "POST"])
@is_logged_in
def create_form():
    if request.method == "POST":
        title = request.form["surveyTitle"]
        form_json = request.form["json"]
        data = json.loads(form_json)

        # Create survey with given information.
        survey_creation_info = {'name': title, 'user': session['user_id'],
                                'date': datetime.now().strftime('%Y-%m-%dT%H:%M')}
        survey_id = create_survey(mysql, survey_creation_info)['surveyID']

        for question in data:
            question_data = {}
            question_data['text'] = question['title']
            if question['type'] == 'multiple_choice':
                question_data['type'] = 'radio'
                question_data['options'] = []
                for option in question['optionList']:
                    question_data['options'].append((option, option))
                add_question(mysql, survey_id, question_data)
            elif question['type'] == 'rating_scale':
                question_data['type'] = 'radio'
                # question_data['options'] =
                add_question(mysql, survey_id, question_data)
            elif question['type'] == 'short_answer':
                question_data['type'] = 'string'
                question_data['options'] = ""
                add_question(mysql, survey_id, question_data)

        return redirect(url_for("view_library"))
    return render_template("survey/new.html", title="Create New Survey")


@app.route("/forms/view/<survey_id>")
@is_logged_in
def view_form(survey_id):
    creator = get_survey_creator(mysql, survey_id)
    if creator is None or session['user_id'] != creator:
        return redirect(url_for("index"))

    questions = get_questions(mysql, survey_id)
    form_name = get_form_name(mysql, survey_id)
    form = build_form(questions)
    return render_template("survey/view.html", title="Survey Detail", form=form, name=form_name, view_only=True)


@app.route("/forms/lookup", methods=["GET", "POST"])
def view_surveys_by_email():
    if request.method == 'POST':
        email_address = request.form['email']
        cur = mysql.connection.cursor()
        result = cur.execute(
            "SELECT surveyName FROM surveys, emails WHERE surveys.surveyID = emails.surveyID AND emails.email=%s",
            [email_address])
        survey_list = {}
        if result > 0:
            survey_list = cur.fetchmany(result)
        return render_template("survey/email_lookup.html", title="Email Lookup", surveys=survey_list, email=email_address)
    return render_template("survey/email_lookup.html", title="Email Lookup", surveys={}, email='')


@is_logged_in
@app.route("/forms/result/<survey_id>")
def view_results(survey_id):
    creator = get_survey_creator(mysql, survey_id)
    if creator is None or session['user_id'] != creator:
        return redirect(url_for("index"))

    questions = get_questions(mysql, survey_id)
    final_questions = {}
    for question in questions:
        if question['questionType'] == 'string' or question['questionType'] == 'integer' or question['questionType'] == 'decimal':
            responses_raw = get_response(mysql, question['questionID'])
            responses = []
            for response in responses_raw:
                responses.append(response['response'])
            final_question = {'title': question['questionTitle'], 'type': 'short_answer', 'responses': responses}
            final_questions[question['questionID']] = final_question
        else:
            options_raw = string_to_list(question['questionOptions'])
            options = {}
            for option in options_raw:
                options[(option[1])] = 0
            responses = get_response(mysql, question['questionID'])
            for response in responses:
                options[response['response']] += 1
            final_question = {'title': question['questionTitle'], 'type': 'multiple_choice', 'optionList': options}
            print(final_question)
    return render_template("survey/result.html", title="View Results", questions=final_questions)


@app.route("/forms/submit", methods=["POST"])
def submit_survey():
    survey_id = request.args.get("survey_id", "")
    if survey_id == "":
        return redirect(url_for("index"))
    questions = get_questions(mysql, survey_id)
    form = build_form(questions)
    if "uuid" not in request.form or validate_hash(mysql, request.form["uuid"]):
        return redirect(url_for("index"))

    if form.validate():
        response = {}
        for pair in request.form:
            if "csrf" not in pair and "uuid" not in pair:
                response[pair] = request.form[pair]
        handle_response(mysql, response, request.form['uuid'])
        return redirect(url_for("survey_completed"))
    else:
        return render_template("survey/view.html", title="Survey Detail", form=form, uuid=request.form["uuid"],
                               surveyID=survey_id)


@app.route("/forms/completed")
def survey_completed():
    return render_template("survey/submitted.html")


@app.errorhandler(404)
def error_404(e):
    return redirect(url_for("index"))


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

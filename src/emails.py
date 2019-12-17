import smtplib
import ssl
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import current_app as app

from src.database_functions import user_id_to_name, generate_hash


def notify_users(mysql, survey_id: int, manager_id: int, employee_list_str: str):
    """Will notify all employees who work under a given manager about a new survey available to take. When the email is
    sent to employees, a unique ID will be given to them such that they are only able to take the survey once. The ID is
     not tied to any specific response. Tracking only if it has been used, and not by who."""
    if not app.config['EMAIL_ENABLED']:  # If email is not enabled, then we don't notify
        return

    employee_list_str.replace(' ', '')
    employee_email_list = employee_list_str.split(',')

    for employee_email in employee_email_list:
        key_for_employee = generate_hash(mysql, survey_id)
        email_user(mysql, employee_email, manager_id, key_for_employee)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO emails (email, surveyID) VALUES (%s, %s)", [employee_email, int(survey_id)])
        mysql.connection.commit()
        cur.close()


def email_user(mysql, destination_email: str, manager_id: int, key: int):
    """Helper function to send an email to the user containing the given unique key which links to the survey."""

    message = generate_email_body(mysql, destination_email, manager_id, key)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(app.config['EMAIL_HOST'], app.config['EMAIL_PORT'], context=context) as server:
        server.login(app.config['EMAIL_ACCOUNT'], app.config['EMAIL_PASSWORD'])
        server.sendmail(
            app.config['EMAIL_ACCOUNT'], destination_email, message.as_string()
        )


def generate_email_body(mysql, destination_email: str, manager_id: int, key: int) -> MIMEMultipart:
    """Generate the email body which contains HTML, and the link to the form for this specific user."""
    message = MIMEMultipart("alternative")
    message["Subject"] = "You Have a New Survey"
    message["From"] = app.config['EMAIL_ACCOUNT']
    message["To"] = destination_email

    link = key_to_link(key)

    text = """\
    You have a new survey available to take.
    You can complete it at this link: \
    """ + link + """
    """

    html_body = email_body(mysql, manager_id, key)

    # Note that the plain text is a fallback in case the HTML does not load.
    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html_body, "html"))
    return message


def key_to_link(key: int):
    """Returns a URL containing the unique key for the survey."""
    return 'http://localhost:5000/forms/validate/' + str(key)


def email_body(mysql, manager_id: int, key: int):
    key_link = key_to_link(key)
    return """ <html lang="en">
        <body>
            <p>
            Hello, <br> <br>
            """+user_id_to_name(mysql, manager_id)+""" has sent you a survey to complete. The results will be completely 
            anonymous, and no personally identifiable information will be available to your manager. Please use this 
            <a href="""+key_link+""">link</a> to access the survey. If you are unable to directly access the link, or need
            to access the survey from another computer, please use this as your unique key: """+str(key)+"""
            <br> <br>
            Thank you.
            </p> 
        </body>
    </html> """

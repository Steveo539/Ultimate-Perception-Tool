import smtplib
import ssl
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import current_app as app

from src.database_functions import user_id_to_name


def notify_users(mysql, survey_id: int, manager_id: int, employee_list: str):
    """Will notify all employees who work under a given manager about a new survey available to take. When the email is
    sent to employees, a unique ID will be given to them such that they are only able to take the survey once. The ID is
     not tied to any specific response. Tracking only if it has been used, and not by who."""
    if not app.config['EMAIL_ENABLED']:  # If email is not enabled, then we don't notify
        return

    # TODO: Get all employees who work under manager. If all_employees is true, then for every employee who is a manager,
    #  add their employees to the email list too. However, every employee should receive at most 1 email.
    employees = []  # list of id's for all the email recipients

    # TODO: Generate a unique key for each user who will have to take the survey
    # TODO: Send an email to each of the users with the unique key
    keys = {}
    for employee_id in employees:
        keys[employee_id] = uuid.uuid4()
        email_user(mysql, employee_id, int(keys[employee_id]))
    pass


def email_user(mysql, manager_id: int, key: int):
    """Helper function to send an email to the user containing the given unique key which links to the survey."""

    user_email = None  # id_to_email(mysql, user_id)  # Fetch user email address
    destination_email = user_email if user_email else 'UltimatePerceptionTool@gmail.com'  # If exists, send to user

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
            """+user_id_to_name(mysql, manager_id)+""" has sent you a survey to complete!
            Please use this <a href="""+key_link+""">link</a> to access the survey
            <br> <br>
            Thank you.
            </p> 
        </body>
    </html> """

import MySQLdb

from src.utility import list_to_string


def get_questions(mysql, form_id):
    try:
        form_id = int(form_id)
    except ValueError:  # Use this to prevent anything but integers being passed to SQL query
        return ""
    cur = mysql.connection.cursor()

    try:  # If there is an exception with the query, fail silently
        cur.execute("SELECT * FROM form_%s", [form_id])
    except (MySQLdb.Error, MySQLdb.Warning):
        return ""

    questions = cur.fetchall()
    cur.close()
    return questions


def add_question(mysql, form_id, question):
    cur = mysql.connection.cursor()
    statement = "INSERT INTO form_" + str(form_id)
    statement += "(type, text, options) VALUES(%s, %s, %s)"
    cur.execute(statement, (question['type'], question['text'], list_to_string(question['options'])))
    mysql.connection.commit()
    cur.close()


def remove_question(mysql, form_id, question_id):
    cur = mysql.connection.cursor()
    statement = "DELETE FROM form_" + str(form_id)
    statement += " WHERE id=%s"
    cur.execute(statement, [question_id])
    mysql.connection.commit()
    cur.close()

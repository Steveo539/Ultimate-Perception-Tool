def get_questions(mysql, form_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM form_%s", [form_id])
    questions = cur.fetchall()
    cur.close()
    return questions


def add_question(mysql, form_id, question):
    cur = mysql.connection.cursor()
    statement = "INSERT INTO form_" + str(form_id)
    statement += "(id, type, text, options) VALUES(%s, %s, %s, %s)"
    cur.execute(statement, (question.id, question.type, question.text, question.options))
    mysql.connection.commit()
    cur.close()


def remove_question(mysql, form_id, question_id):
    cur = mysql.connection.cursor()
    statement = "DELETE FROM form_" + str(form_id)
    statement += " WHERE id=%s"
    cur.execute(statement, [question_id])
    mysql.connection.commit()
    cur.close()

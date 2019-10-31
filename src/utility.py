from forms import *


def load_database_info():
    info = {}
    try:
        db_config = open('../db.info', 'r')
    except IOError:
        print('ERROR: Invalid \'db.info\'...exiting')
        return None

    info['secret_key'] = db_config.readline().strip()
    info['host'] = db_config.readline().strip()
    info['user'] = db_config.readline().strip()
    info['password'] = db_config.readline().strip()
    info['db'] = db_config.readline().strip()
    db_config.close()
    return info


def get_questions(mysql, form_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM form_%s", [form_id])
    questions = cur.fetchall()
    cur.close()
    return questions


def build_strings(questions):
    strings = []
    for question in questions:
        if question.type == 'string':
            entry = StringForm()
            entry.string.label = question.text
            entry.string.id = question.id
            strings.append(entry)
    return strings


def build_integers(questions):
    integers = []
    for question in questions:
        if question.type == 'integer':
            entry = IntegerForm()
            entry.integer.label = question.text
            entry.integer.id = question.id
            integers.append(entry)
    return integers


def build_decimals(questions):
    decimals = []
    for question in questions:
        if question.type == 'decimal':
            entry = DecimalForm()
            entry.decimal.label = question.text
            entry.decimal.id = question.id
            decimals.append(entry)
    return decimals


def build_radios(questions):
    radios = []
    for question in questions:
        if question.type == 'radio':
            entry = RadioForm()
            entry.radio.label = question.text
            entry.radio.id = question.id
            entry.radio.choices = question.options
            radios.append(entry)
    return radios


def build_selects(questions):
    selects = []
    for question in questions:
        if question.type == 'select':
            entry = SelectForm()
            entry.select.label = question.text
            entry.select.id = question.id
            entry.select.choices = question.options
            selects.append(entry)
    return selects


def check_if_unused(fieldlist):
    for field in fieldlist:
        if field.label == "Placeholder":
            return True
        return False


def purge_unused_fields(form):
    if check_if_unused(form.strings.entries):
        del form.strings
    if check_if_unused(form.integers.entries):
        del form.integers
    if check_if_unused(form.decimals.entries):
        del form.decimals
    if check_if_unused(form.radios.entries):
        del form.radios
    if check_if_unused(form.selects.entries):
        del form.selects
    return form


def build_form(questions):
    form = MainForm()
    form.strings.entries = build_strings(questions)
    form.integers.entries = build_integers(questions)
    form.decimals.entries = build_decimals(questions)
    form.radios.entries = build_radios(questions)
    form.selects.entries = build_selects(questions)
    form = purge_unused_fields(form)
    return form

from src.forms import MainForm, SelectForm, RadioForm, DecimalForm, IntegerForm, StringForm
from src.utility import string_to_list


def build_strings(questions):
    strings = []
    for question in questions:
        if question["questionType"] == 'string':
            entry = StringForm()
            entry.string.label = question["questionTitle"]
            entry.string.id = question["questionID"]
            strings.append(entry)
    return strings


def build_integers(questions):
    integers = []
    for question in questions:
        if question["questionType"] == 'integer':
            entry = IntegerForm()
            entry.integer.label = question["questionTitle"]
            entry.integer.id = question["questionID"]
            integers.append(entry)
    return integers


def build_decimals(questions):
    decimals = []
    for question in questions:
        if question["questionType"] == 'decimal':
            entry = DecimalForm()
            entry.decimal.label = question["questionTitle"]
            entry.decimal.id = question["questionID"]
            decimals.append(entry)
    return decimals


def build_radios(questions):
    radios = []
    for question in questions:
        if question["questionType"] == 'radio':
            entry = RadioForm()
            entry.radio.label = question["questionTitle"]
            entry.radio.id = question["questionID"]
            entry.radio.choices = string_to_list(question["questionOptions"])
            radios.append(entry)
    return radios


def build_selects(questions):
    selects = []
    for question in questions:
        if question["questionType"] == 'select':
            entry = SelectForm()
            entry.select.label = question["questionTitle"]
            entry.select.id = question["questionID"]
            entry.select.choices = string_to_list(question["questionOptions"])
            selects.append(entry)
    return selects


def purge_unused_fields(form):
    if len(form.strings.entries) < 1:
        del form.strings
    if len(form.integers.entries) < 1:
        del form.integers
    if len(form.decimals.entries) < 1:
        del form.decimals
    if len(form.radios.entries) < 1:
        del form.radios
    if len(form.selects.entries) < 1:
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

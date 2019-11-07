from src.forms import MainForm, SelectForm, RadioForm, DecimalForm, IntegerForm, StringForm
from src.utility import string_to_list


def build_strings(questions):
    strings = []
    for question in questions:
        if question["type"] == 'string':
            entry = StringForm()
            entry.string.label = question["text"]
            entry.string.id = question["id"]
            strings.append(entry)
    return strings


def build_integers(questions):
    integers = []
    for question in questions:
        if question["type"] == 'integer':
            entry = IntegerForm()
            entry.integer.label = question["text"]
            entry.integer.id = question["id"]
            integers.append(entry)
    return integers


def build_decimals(questions):
    decimals = []
    for question in questions:
        if question["type"] == 'decimal':
            entry = DecimalForm()
            entry.decimal.label = question["text"]
            entry.decimal.id = question["id"]
            decimals.append(entry)
    return decimals


def build_radios(questions):
    radios = []
    for question in questions:
        if question["type"] == 'radio':
            entry = RadioForm()
            entry.radio.label = question["text"]
            entry.radio.id = question["id"]
            entry.radio.choices = string_to_list(question["options"])
            radios.append(entry)
    return radios


def build_selects(questions):
    selects = []
    for question in questions:
        if question["type"] == 'select':
            entry = SelectForm()
            entry.select.label = question["text"]
            entry.select.id = question["id"]
            entry.select.choices = string_to_list(question["options"])
            selects.append(entry)
    return selects


# def purge_unused_fields(form):
#     if form.strings.entries[0].string.label == "Placeholder":
#         del form.strings
#     if form.integers.entries[0].integer.label == "Placeholder":
#         del form.integers
#     if form.decimals.entries[0].decimal.label == "Placeholder":
#         del form.decimals
#     if form.radios.entries[0].radio.label == "Placeholder":
#         del form.radios
#     if form.selects.entries[0].select.label == "Placeholder":
#         del form.selects
#     return form

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

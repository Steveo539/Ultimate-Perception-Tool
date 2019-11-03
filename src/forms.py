from wtforms import DecimalField, StringField, IntegerField, RadioField, SelectField, FieldList, FormField
from flask_wtf import FlaskForm


class SelectForm(FlaskForm):
    select = SelectField("Placeholder", choices=[])


class SelectFormList(FlaskForm):
    entries = FieldList(FormField(SelectForm))


class DecimalForm(FlaskForm):
    decimal = DecimalField("Placeholder")


class DecimalFormList(FlaskForm):
    entries = FieldList(FormField(DecimalForm))


class IntegerForm(FlaskForm):
    integer = IntegerField("Placeholder")


class IntegerFormList(FlaskForm):
    entries = FieldList(FormField(IntegerForm))


class RadioForm(FlaskForm):
    radio = RadioField("Placeholder", choices=[])


class RadioFormList(FlaskForm):
    entries = FieldList(FormField(RadioForm))


class StringForm(FlaskForm):
    string = StringField("Placeholder")


class StringFormList(FlaskForm):
    entries = FieldList(FormField(StringForm))


class MainForm(FlaskForm):
    strings = FormField(StringFormList)
    radios = FormField(RadioFormList)
    integers = FormField(IntegerFormList)
    decimals = FormField(DecimalFormList)
    selects = FormField(SelectFormList)
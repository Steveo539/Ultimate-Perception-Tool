from wtforms import DecimalField, StringField, IntegerField, RadioField, SelectField, FieldList, FormField, PasswordField, validators
from flask_wtf import FlaskForm


class RegisterForm(FlaskForm):
    name = StringField("Name", [validators.Length(min=1, max=149)])
    username = StringField("Username", [validators.Length(min=4, max=29)])
    email = StringField("Email", [validators.Length(min=6, max=99), validators.email(message="Must be a valid email")])
    position = StringField("Position Title", [validators.length(min=1, max=99)])
    company = IntegerField("Company ID", [validators.DataRequired(message="Enter your company ID")])
    password = PasswordField("Password", [validators.DataRequired(), validators.EqualTo("confirm", message="Passwords don't match"), validators.Length(min=5, max=50)])
    confirm = PasswordField("Confirm Password", [validators.DataRequired()])


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
# modules
from flask_wtf import Form
from wtforms.fields import RadioField, StringField
from wtforms.widgets import TextInput
from wtforms import Field, validators


class NextOpenField(Field):
    widget = TextInput()


class NextCloseField(Field):
    widget = TextInput()


class ExceptionsField(Field):
    widget = TextInput()


class OfficeHoursForm(Form):

    next_open = NextOpenField('')

    next_start_date = StringField('Start Date', validators=[validators.DataRequired()])

    next_monday_open = StringField('Monday', validators=[validators.DataRequired()])
    next_monday_close = StringField(validators=[validators.DataRequired()])

    next_tuesday_open = StringField('Tuesday', validators=[validators.DataRequired()])
    next_tuesday_close = StringField(validators=[validators.DataRequired()])

    next_wednesday_open = StringField('Wednesday', validators=[validators.DataRequired()])
    next_wednesday_close = StringField(validators=[validators.DataRequired()])

    next_thursday_open = StringField('Thursday', validators=[validators.DataRequired()])
    next_thursday_close = StringField(validators=[validators.DataRequired()])

    next_friday_open = StringField('Friday', validators=[validators.DataRequired()])
    next_friday_close = StringField(validators=[validators.DataRequired()])

    next_saturday_open = StringField(label='Saturday', validators=[validators.DataRequired()])
    next_saturday_close = StringField(validators=[validators.DataRequired()])

    next_sunday_open = StringField('Sunday', validators=[validators.DataRequired()])
    next_sunday_close = StringField(validators=[validators.DataRequired()])

    next_closed_for_chapel = RadioField("Office closed for chapel", choices=[('Yes', 'Yes'), ('No', 'No')])

    next_close = NextCloseField()

    exceptions = ExceptionsField("Exception Date")

    # Manually override validate, in order to check the dates
    def validate(self):
        pass

# modules
from flask_wtf import Form
from wtforms.fields import RadioField, StringField
from wtforms.widgets import TextInput
from wtforms import Field, validators


class NextOpenField(Field):
    widget = TextInput()


class NextCloseField(Field):
    widget = TextInput()


class TimeField(StringField):
    widget = TextInput()


class DatePickerField(StringField):
    widget = TextInput()


class ExceptionsField(Field):
    widget = TextInput()


class OfficeHoursForm(Form):

    website = StringField('Website URL')
    location = StringField('Office location')
    phone_number = StringField('Phone number')

    next_open = NextOpenField('')

    next_start_date = DatePickerField('Start Date', validators=[validators.DataRequired()])

    next_closed_for_chapel = RadioField("Office closed for chapel", choices=[('Yes', 'Yes'), ('No', 'No')])

    next_monday_open = TimeField('Monday', validators=[validators.DataRequired()])
    next_monday_close = TimeField(validators=[validators.DataRequired()])

    next_tuesday_open = TimeField('Tuesday', validators=[validators.DataRequired()])
    next_tuesday_close = TimeField(validators=[validators.DataRequired()])

    next_wednesday_open = TimeField('Wednesday', validators=[validators.DataRequired()])
    next_wednesday_close = TimeField(validators=[validators.DataRequired()])

    next_thursday_open = TimeField('Thursday', validators=[validators.DataRequired()])
    next_thursday_close = TimeField(validators=[validators.DataRequired()])

    next_friday_open = TimeField('Friday', validators=[validators.DataRequired()])
    next_friday_close = TimeField(validators=[validators.DataRequired()])

    next_saturday_open = TimeField(label='Saturday', validators=[validators.DataRequired()])
    next_saturday_close = TimeField(validators=[validators.DataRequired()])

    next_sunday_open = TimeField('Sunday', validators=[validators.DataRequired()])
    next_sunday_close = TimeField(validators=[validators.DataRequired()])

    next_close = NextCloseField()

    exceptions = ExceptionsField("Exception Date")

    # Manually override validate, in order to check the dates
    def validate(self):
        pass

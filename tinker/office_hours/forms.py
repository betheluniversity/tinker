# modules
from flask.ext.wtf import Form
from wtforms.fields.html5 import DateField, DateTimeField
from wtforms.fields import FormField, RadioField
from wtforms import Field
from wtforms import validators


class TimeOpenField(Field):
    def __init__(self, label=None, validators=None, filters=tuple(),
                 description='', id=None, default=None, widget=None,
                 _form=None, _name=None, _prefix='', _translations=None, format='%I:%M %p'):


        self.default = default
        self.description = description
        self.filters = filters
        self.flags = None
        self.name = _prefix + _name
        self.short_name = _name
        self.type = type(self).__name__
        self.validators = validators or list(self.validators)
        self.format = format

        self.id = id or self.name
        self.label = label

class TimeCloseField(Field):
    def __init__(self, label=None, validators=None, filters=tuple(),
                 description='', id=None, default=None, widget=None,
                 _form=None, _name=None, _prefix='', _translations=None, format='%I:%M %p'):
        self.default = default
        self.description = description
        self.filters = filters
        self.flags = None
        self.name = _prefix + _name
        self.short_name = _name
        self.type = type(self).__name__
        self.validators = validators or list(self.validators)
        self.format = format

        self.id = id or self.name
        self.label = label


class ExceptionForm(Form):
    date = DateField("Exception Date", format='%m-%d-%Y')
    open = TimeOpenField(label='Open from', validators=[validators.DataRequired()])
    close = TimeCloseField(validators=[validators.DataRequired()])


class OfficeHoursForm(Form):
    next_start_date = DateField('Start Date', format='%m-%d-%Y %I:%M:%s', validators=[validators.DataRequired()])

    next_monday_open = TimeField(label='Monday', validators=[validators.DataRequired()])
    next_monday_close = TimeField(validators=[validators.DataRequired()])

    next_tuesday_open = TimeField(label='Tuesday', validators=[validators.DataRequired()])
    next_tuesday_close = TimeField(validators=[validators.DataRequired()])

    next_wednesday_open = TimeField(label='Wednesday', validators=[validators.DataRequired()])
    next_wednesday_close = TimeField(validators=[validators.DataRequired()])

    next_thursday_open = TimeField(label='Thursday', validators=[validators.DataRequired()])
    next_thursday_close = TimeField(validators=[validators.DataRequired()])

    next_friday_open = TimeField(label='Friday', validators=[validators.DataRequired()])
    next_friday_close = TimeField(validators=[validators.DataRequired()])

    next_saturday_open = TimeField(label='Saturday', validators=[validators.DataRequired()])
    next_saturday_close = TimeField(validators=[validators.DataRequired()])

    next_sunday_open = TimeField(label='Sunday', validators=[validators.DataRequired()])
    next_sunday_close = TimeField(validators=[validators.DataRequired()])

    next_closed_for_chapel = RadioField("Office closed for chapel", choices=[('Yes', 'Yes'), ('No', 'No')])
    exceptions = FormField(ExceptionForm)


    # Manually override validate, in order to check the dates
    def validate(self):
        pass
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

        self.id = id or self.name
        self.label = label

class TimeCloseField(DateTimeField):
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

        self.id = id or self.name
        self.label = label


class HoursGroupForm(Form):
    start_date = DateField('Start Date', format='%m-%d-%Y %I:%M:%s', validators=[validators.DataRequired()])

    monday_open = TimeOpenField(label='Monday', validators=[validators.DataRequired()])
    monday_close = TimeCloseField(validators=[validators.DataRequired()])

    tuesday_open = TimeOpenField(label='Tuesday', validators=[validators.DataRequired()])
    tuesday_close = TimeCloseField(validators=[validators.DataRequired()])

    wednesday_open = TimeOpenField(label='Wednesday', validators=[validators.DataRequired()])
    wednesday_close = TimeCloseField(validators=[validators.DataRequired()])

    thursday_open = TimeOpenField(label='Thursday', validators=[validators.DataRequired()])
    thursday_close = TimeCloseField(validators=[validators.DataRequired()])

    friday_open = TimeOpenField(label='Friday', validators=[validators.DataRequired()])
    friday_close = TimeCloseField(validators=[validators.DataRequired()])

    saturday_open = TimeOpenField(label='Saturday', validators=[validators.DataRequired()])
    saturday_close = TimeCloseField(validators=[validators.DataRequired()])

    sunday_open = TimeOpenField(label='Sunday', validators=[validators.DataRequired()])
    sunday_close = TimeCloseField(validators=[validators.DataRequired()])

    closed_for_chapel = RadioField("Office closed for chapel", choices=[('Yes', 'Yes'), ('No', 'No')])


class ExceptionForm(Form):
    date = DateField("Exception Date", format='%m-%d-%Y')
    open = TimeOpenField(label='Open from', validators=[validators.DataRequired()])
    close = TimeCloseField(validators=[validators.DataRequired()])


class OfficeHoursForm(Form):
    next = FormField(HoursGroupForm)
    exceptions = FormField(ExceptionForm)


    # Manually override validate, in order to check the dates
    def validate(self):
        pass
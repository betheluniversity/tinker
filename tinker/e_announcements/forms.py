# coding: utf-8

# python

# modules
from flask.ext.wtf import Form
from wtforms import TextField
from wtforms import SelectMultipleField
from wtforms import TextAreaField
from wtforms import DateField
from wtforms import Field
from wtforms import validators
from wtforms import widgets

# local
from tinker import app
from tinker.web_services import get_client, read


def get_md(metadata_path):
    md = read(metadata_path, 'metadataset')
    return md.asset.metadataSet.dynamicMetadataFieldDefinitions.dynamicMetadataFieldDefinition


def get_audience_choices():

    data = get_md("/Targeted")
    audience_list = data[0].possibleValues.possibleValue
    audience = []
    for item in audience_list:
        if item.value != "":
            audience.append(item.value)

    banner_roles_sort_mapping = {
        'STUDENT-CAS': 1,
        'STUDENT-CAPS': 2,
        'STUDENT-GS': 3,
        'STUDENT-BSSP-TRADITIONAL': 4,
        'STUDENT-BSSP-DISTANCE': 5,
        'STUDENT-BSSD-TRADITIONAL': 6,
        'STUDENT-BSSD-DISTANCE': 7,
        'STUDENT-BSOE-TRADITIONAL': 8,
        'STUDENT-BSOE-DISTANCE': 9,
        'FACULTY-CAS': 10,
        'FACULTY-CAPS': 11,
        'FACULTY-GS': 12,
        'FACULTY-BSSP': 13,
        'FACULTY-BSSD': 14,
        'STAFF-STP': 15,
        'STAFF-SD': 16
    }

    # sort list
    audience = sorted(audience, key=lambda x: banner_roles_sort_mapping[x])

    # convert back to the tuple format
    audience = [(value, value) for value in audience]
    return audience


# Special class to know when to include the class for a ckeditor wysiwyg
class CKEditorTextAreaField(TextAreaField):
    pass


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class HeadingField(Field):

    def __init__(self, label=None, validators=None, filters=tuple(),
                 description='', id=None, default=None, widget=None,
                 _form=None, _name=None, _prefix='', _translations=None):

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

    def __unicode__(self):
        return None

    def __str__(self):
        return None

    def __html__(self):
        return None


#####################
# Faculty Bio Forms
#####################
# Special class to know when to include the class for a ckeditor wysiwyg
class DummyField(TextAreaField):
    pass


class EAnnouncementsForm(Form):

    announcement_information = HeadingField(label="Announcement Information")
    title = TextField('Title', validators=[validators.DataRequired()])
    message = CKEditorTextAreaField('Message', description="Announcements are limited to 200 words. Exceptions will be granted if deemed appropriate by the Office of Communications and Marketing. Contact e-announcements@bethel.edu if you need an exception to this limit.\nMessage Editing: Pressing 'Enter' starts a new paragraph. Hold 'Shift' while pressing 'Enter' to start a new line.", validators=[validators.DataRequired()])
    department = TextField('Sponsoring Department, Office, or Group', validators=[validators.DataRequired()])

    first = DateField("First Date", format="%m-%d-%Y", validators=[validators.DataRequired()])
    second = DateField("Optional Second Date. This date should be later than the first date.", format="%m-%d-%Y", validators=[validators.Optional()])

    banner_roles = MultiCheckboxField(label='', choices=get_audience_choices())

    # Manually override validate, in order to check the dates
    def validate(self):
        if not Form.validate(self):
            return False
        result = True

        if self.second.data:
            if self.first.data >= self.second.data:
                self.first.errors.append('The first date must come before the second date.')
                result = False

        return result
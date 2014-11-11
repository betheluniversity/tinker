# coding: utf-8

#python
import datetime

#modules
from flask.ext.wtf import Form
from wtforms import TextField
from wtforms import SelectMultipleField
from wtforms import TextAreaField
from wtforms import DateField
from wtforms import Field
from wtforms.validators import Required
from wtforms.validators import Optional


#local
from tinker import app
from tinker.tools import *
##from tinker import cache
from tinker.web_services import get_client, read

### Currently is broken. Tinker does not have permissions to access data definitions
def get_md(metadata_path):
    #todo move this to a read()
    auth = app.config['CASCADE_LOGIN']

    identifier = {
        'path': {
            'path': metadata_path,
            'siteName': 'Public'
        },
        'type': 'metadataset',
    }

    client = get_client()
    md = client.service.read(auth, identifier)
    return md.asset.metadataSet.dynamicMetadataFieldDefinitions.dynamicMetadataFieldDefinition

def get_audience_choices():
    data = get_md("/Targeted")
    audience_list = data[0].possibleValues.possibleValue

    audience = []
    for item in audience_list:
        if item.value != "":
            audience.append((item.value, item.value))

    return audience

##Special class to know when to include the class for a ckeditor wysiwyg, doesn't need to do anything
##aside from be a marker label
class CKEditorTextAreaField(TextAreaField):
    pass


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
##Faculty Bio Forms
#####################

##Special class to know when to include the class for a ckeditor wysiwyg, doesn't need to do anything
##aside from be a marker label
class DummyField(TextAreaField):
    pass

class EAnnouncementsForm(Form):

    announcement_information = HeadingField(label="Announcement Information")

    title = TextField('Title', validators=[Required()])
    message = CKEditorTextAreaField('Message', description="Announcements are limited to 200 words. Exceptions will be granted if deemed appropriate by the Office of Communications and Marketing. Contact e-announcements@bethel.edu if you need an exception to this limit.\nMessage Editing: Pressing 'Enter' starts a new paragraph. Hold 'Shift' while pressing 'Enter' to start a new line.", validators=[Required()])
    department = TextField('Sponsoring Department, Office, or Group', validators=[Required()])
    audience = SelectMultipleField('Audience', description="To choose more than one audience, hold down the control key while highlighting the audiences your message should be sent to. (Apple users should hold down the Apple/command key instead of the control key.)", choices=get_audience_choices(), validators=[Required()])

    first = DateField("First Date", format="%m-%d-%Y")
    second = DateField("Optional Second Date", format="%m-%d-%Y", validators=[Optional()] )

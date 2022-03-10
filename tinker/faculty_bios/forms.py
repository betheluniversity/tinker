# Packages
import requests
from flask import session
from flask_wtf import Form
from flask_wtf.file import FileField
from wtforms import Field, HiddenField, SelectMultipleField, StringField, TextAreaField, RadioField, ValidationError, validators

# Local
from tinker.faculty_bios.faculty_bio_controller import FacultyBioController


# Special class to know when to include the class for a ckeditor wysiwyg, doesn't need to do anything
# aside from be a marker label
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
# #Faculty Bio Forms
#####################

# Special class to know when to include the class for a ckeditor wysiwyg, doesn't need to do anything
# aside from be a marker label
class DummyField(TextAreaField):
    pass


def validate_username(form, field):
    username = field.data
    url = "http://wsapi.bethel.edu/username/%s/roles" % username
    req = FacultyBioController().tinker_requests(url)

    content = req.content
    if content == str({}):
        raise ValidationError("Enter the username you use to login to MyBethel and don't include '@bethel.edu'.")


class FacultyBioForm(Form):
    fac_bio_controller = FacultyBioController()
    user_can_edit_image = fac_bio_controller.should_be_able_to_edit_image()

    # todo: this is for jenny vang. This should be removed when she is done.
    # this allows jenny vang to not have to fill out every field
    if session['username'] == 'jev24849':
        if user_can_edit_image:
            image = FileField("Image")
        else:
            image = HiddenField("Image")

        image_url = HiddenField("Image URL")

        first = StringField('Faculty first name')
        last = StringField('Faculty last name')
        author_faculty = StringField("Faculty member's username", description="Enter your Bethel username.")

        if 'Tinker Faculty Bios - Admin' in session['groups'] or 'Administrators' in session['groups'] \
                or 'Tinker Faculty Bios - CAS' in session['groups'] \
                or 'Tinker Faculty Bios - CAPS and GS' in session['groups'] \
                or 'Tinker Faculty Bios - SEM' in session['groups']:
            courseleaf_user = RadioField('Add this user to CourseLeaf (catalog.bethel.edu)', default='Yes', choices=[('Yes', 'Yes'), ('No', 'No')])

        faculty_location = SelectMultipleField('Location', choices=[('St. Paul', 'St. Paul'), ('San Diego', 'San Diego'), ('Online', 'Online')], validators=[validators.DataRequired()])
        highlight = TextAreaField('Highlight text', description="This text will appear on faculty listing pages as a short snippet about you!")

        new_job_titles = StringField('')

        email = StringField('Email')
        started_at_bethel = StringField('Started at Bethel in', description="Enter a year")

        degree = DummyField('')

        biography = CKEditorTextAreaField('Biography')
        courses = CKEditorTextAreaField('Courses Taught')
        awards = CKEditorTextAreaField('Awards')
        publications = CKEditorTextAreaField('Publications')
        presentations = CKEditorTextAreaField('Presentations')
        certificates = CKEditorTextAreaField('Certificates and licenses')
        organizations = CKEditorTextAreaField('Professional Organizations, Committees, and Boards')
        hobbies = CKEditorTextAreaField('Hobbies and interests')
        areas = TextAreaField('Areas of expertise')
        research_interests = TextAreaField('Research interests')
        teaching_specialty = TextAreaField('Teaching specialty')

        quote = StringField('Quote')

        website = StringField('Professional website or blog')
    else:
        if user_can_edit_image:
            image = FileField("Image")
        else:
            image = HiddenField("Image")

        image_url = HiddenField("Image URL")

        first = StringField('Faculty first name', validators=[validators.DataRequired()])
        last = StringField('Faculty last name', validators=[validators.DataRequired()])
        author_faculty = StringField("Faculty member's username", validators=[validators.DataRequired(), validate_username],
                             description="Enter your Bethel username.")

        if 'Tinker Faculty Bios - Admin' in session['groups'] or 'Administrators' in session['groups'] \
                or 'Tinker Faculty Bios - CAS' in session['groups'] \
                or 'Tinker Faculty Bios - CAPS and GS' in session['groups'] \
                or 'Tinker Faculty Bios - SEM' in session['groups']:
            courseleaf_user = RadioField('Add this user to CourseLeaf (catalog.bethel.edu)', default='Yes', choices=[('Yes', 'Yes'), ('No', 'No')])

        faculty_location = SelectMultipleField('Location',
                                               choices=[('St. Paul', 'St. Paul'), ('Online', 'Online')], validators=[validators.DataRequired()])
        highlight = TextAreaField('Highlight text',
                                  description="This text will appear on faculty listing pages as a short snippet about you!",
                                  validators=[validators.DataRequired()])

        new_job_titles = StringField('')

        email = StringField('Email', validators=[validators.DataRequired()])
        started_at_bethel = StringField('Started at Bethel in', validators=[validators.DataRequired()],
                                        description="Enter a year")

        degree = DummyField('')

        biography = CKEditorTextAreaField('Biography')
        courses = CKEditorTextAreaField('Courses Taught')
        awards = CKEditorTextAreaField('Awards')
        publications = CKEditorTextAreaField('Publications')
        presentations = CKEditorTextAreaField('Presentations')
        certificates = CKEditorTextAreaField('Certificates and licenses')
        organizations = CKEditorTextAreaField('Professional Organizations, Committees, and Boards')
        hobbies = CKEditorTextAreaField('Hobbies and interests')
        areas = TextAreaField('Areas of expertise')
        research_interests = TextAreaField('Research interests')
        teaching_specialty = TextAreaField('Teaching specialty')

        quote = StringField('Quote')

        website = StringField('Professional website or blog')

    # Manually override validate, in order to check the 3 headers below
    def validate(self):
        if not Form.validate(self):
            return False
        else:
            return True

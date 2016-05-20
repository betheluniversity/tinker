__author__ = 'ces55739'

import datetime
import re

from flask import session
from flask import render_template
from tinker import app
from tinker.cascade_tools import *

from tinker.tinker_base import TinkerBase

BRM = [
        'CAS',
        'CAPS',
        'GS',
        'BSSP-TRADITIONAL',
        'BSSP-DISTANCE',
        'BSSD-TRADITIONAL',
        'BSSD-DISTANCE',
        'BSOE-TRADITIONAL',
        'BSOE-DISTANCE',
        'CAS',
        'CAPS',
        'GS',
        'BSSP',
        'BSSD',
        'St. Paul',
        'San Diego'
]

class EAnnouncementsBase(TinkerBase):

    def __init__(self):
        super(EAnnouncementsBase, self).__init__()
        self.brm = BRM

    def inspect_child(self, child):

        try:
            author = child.find('author').text
        except AttributeError:
            author = None
        username = session['username']

        if (author is not None and username == author) or username in app.config['E_ANN_ADMINS']:
            try:
                return self._iterate_child_xml(child, author)
            except AttributeError:
                # not a valid e-ann block
                print 'bad'
                return None
        else:
            return None

    def _iterate_child_xml(self, child, author):

        first = child.find('system-data-structure/first-date').text
        second = child.find('system-data-structure/second-date').text
        first_date_object = datetime.datetime.strptime(first, '%m-%d-%Y')
        first_date = first_date_object.strftime('%A %B %d, %Y')
        first_date_past = first_date_object < datetime.datetime.now()

        second_date = ''
        second_date_past = ''
        if second:
            second_date_object = datetime.datetime.strptime(second, '%m-%d-%Y')
            second_date = second_date_object.strftime('%A %B %d, %Y')
            second_date_past = second_date_object < datetime.datetime.now()

        roles = []
        values = child.find('dynamic-metadata')
        for value in values:
            if value.tag == 'value':
                roles.append(value.text)

        message = ''
        message = self.recurse_wysiwyg_xml(child.find('system-data-structure/message'))

        try:
            workflow_status = child.find('workflow').find('status').text
        except AttributeError:
            workflow_status = None

        page_values = {
            'author': author,
            'id': child.attrib['id'] or "",
            'title': child.find('title').text or None,
            'created-on': child.find('created-on').text or None,
            'first_date': first_date,
            'second_date': second_date,
            'message': message,
            'roles': roles,
            'workflow_status': workflow_status,
            'first_date_past': first_date_past,
            'second_date_past': second_date_past
        }
        return page_values

    def recurse_wysiwyg_xml(self, node):
        return_string = ''
        for child in node:
            child_text = ''
            if child.text:
                child_text = child.text

            # recursively renders children
            try:
                if child.tag == 'a':
                    return_string += '<%s href="%s">%s%s</%s>' % (child.tag, child.attrib['href'], child_text, self.recurse_wysiwyg_xml(child), child.tag)
                else:
                    return_string += '<%s>%s%s</%s>' % (child.tag, child_text, self.recurse_wysiwyg_xml(child), child.tag)
            except:
                # gets the basic text
                if child_text:
                    if child.tag == 'a':
                        return_string += '<%s href="%s">%s</%s>' % (child.tag, child.attrib['href'], child_text, child.tag)
                    else:
                        return_string += '<%s>%s</%s>' % (child.tag, child_text, child.tag)

            # gets the text that follows the children
            if child.tail:
                return_string += child.tail

        return return_string

    ##########################################################
    # Todo: every method below should probably be cleaned up
    ###########################################################
    def get_add_data(self, lists, form):

        # A dict to populate with all the interesting data.
        add_data = {}

        for key in form.keys():
            if key in lists:
                add_data[key] = form.getlist(key)
            else:
                add_data[key] = form[key]

        # Create the system-name from title, all lowercase
        system_name = add_data['title'].lower().replace(' ', '-')

        # Now remove any non a-z, A-Z, 0-9
        system_name = re.sub(r'[^a-zA-Z0-9-]', '', system_name)

        add_data['system_name'] = system_name

        return add_data

    def get_e_announcement_publish_workflow(self, title=""):

        name = "New E-announcement Submission"
        if title:
            name += ": " + title
        workflow = {
            "workflowName": name,
            "workflowDefinitionId": app.config['E_ANNOUCNEMENT_WORKFLOW_ID'],
            "workflowComments": "Send e-announcement for approval"
        }
        return workflow

    def validate_form(self, rform):

        from forms import EAnnouncementsForm
        form = EAnnouncementsForm()

        # todo move to TinkerBase?
        if not form.validate_on_submit():
            if 'e_announcement_id' in rform.keys():
                e_announcement_id = rform['e_announcement_id']
            else:
                new_form = True
            # bring in the mapping
            brm = self.brm
            return render_template('e-announcements-form.html', **locals())

    def get_e_announcement_parent_folder(self, date):
        # break the date into Year/month
        split_date = date.split("-")
        month = self.convert_month_num_to_name(split_date[0])
        year = split_date[2]

        # check if the folders exist
        self.create_folder("e-announcements/" + year)
        self.create_folder("e-announcements/" + year + "/" + month)

        return "e-announcements/" + year + "/" + month

    def update_structure(self, e_announcement_data, sdata, rform, e_announcement_id=None):
        """
         Could this be cleaned up at all?
        """

        title = self.format_title(rform['title'])

        # todo can we simplify or genericize this?
        add_data = self.get_add_data(['banner_roles'], rform)
        workflow = self.get_e_announcement_publish_workflow(title)

        parent_folder = self.get_e_announcement_parent_folder(add_data['first_date'])

        add_data['name'] = session['name']
        add_data['email'] = session['user_email']

        self.update(e_announcement_data, 'message', escape_wysiwyg_content(add_data['message']))
        self.update(e_announcement_data, 'first-date', add_data['first_date'])
        self.update(e_announcement_data, 'second-date', add_data['second_date'])
        self.update(sdata, 'name', add_data['name'])
        self.update(e_announcement_data, 'email', add_data['email'])


        self.update(e_announcement_data, 'parentFolderPath', parent_folder)
        self.update(e_announcement_data, 'title', add_data['title'])
        self.update(e_announcement_data, 'author', session['username'])


        # # todo have to figure out how to do this
        # # create the dynamic metadata dict
        # dynamic_fields = {
        #     'dynamicField': [
        #         dynamic_field('banner-roles', add_data['banner_roles']),
        #     ],
        # }


        if e_announcement_id:
            self.update(e_announcement_data, 'id', e_announcement_id)
            # todo: does this call every time just in case it moved?
            self.move(e_announcement_id, parent_folder)

        return e_announcement_data
__author__ = 'ces55739'

import datetime
import re

from flask import session
from tinker import app
from tinker.cascade_tools import *


class EAnnouncementHelper():

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
    def get_add_data(lists, form):

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

    def get_e_announcement_publish_workflow(title=""):

        name = "New E-announcement Submission"
        if title:
            name += ": " + title
        workflow = {
            "workflowName": name,
            "workflowDefinitionId": app.config['E_ANNOUCNEMENT_WORKFLOW_ID'],
            "workflowComments": "Send e-announcement for approval"
        }
        return workflow

    def get_e_announcement_structure(add_data, username, workflow=None, e_announcement_id=None):
        """
         Could this be cleaned up at all?
        """

        # Create a list of all the data nodes
        structured_data = [
            structured_data_node("message", escape_wysiwyg_content(add_data['message'])),
            structured_data_node("first-date", add_data['first']),
            structured_data_node("second-date", add_data['second']),
            structured_data_node("name", add_data['name']),
            structured_data_node("email", add_data['email']),
        ]

        # Wrap in the required structure for SOAP
        structured_data = {
            'structuredDataNodes': {
                'structuredDataNode': structured_data,
            },
            'definitionPath': 'E-Announcement'
        }

        # create the dynamic metadata dict
        dynamic_fields = {
            'dynamicField': [
                dynamic_field('banner-roles', add_data['banner_roles']),
            ],
        }

        parent_folder = get_e_announcement_parent_folder(add_data['first'])
        asset = {
            'xhtmlDataDefinitionBlock': {
                'name': add_data['system_name'],
                'siteId': app.config['SITE_ID'],
                'parentFolderPath': parent_folder,
                'metadataSetPath': "/Targeted",
                'structuredData': structured_data,
                'metadata': {
                    'title': add_data['title'],
                    'author': username,
                    'dynamicFields': dynamic_fields,
                }
            },
            'workflowConfiguration': workflow
        }

        if e_announcement_id:
            asset['xhtmlDataDefinitionBlock']['id'] = e_announcement_id
            resp = move(e_announcement_id, parent_folder)

        return asset
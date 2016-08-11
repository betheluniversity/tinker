import urllib2
import re
import time
import cgi
from xml.etree import ElementTree as ET
import requests
import datetime
import fnmatch
import hashlib
import os
from functools import wraps
from subprocess import call

# flask
from flask import request
from flask import session
from flask import current_app
from flask import render_template
from flask import json as fjson
from flask import Response

from bu_cascade.cascade_connector import Cascade
from bu_cascade.assets.block import Block
from bu_cascade.assets.page import Page
from bu_cascade.assets.metadata_set import MetadataSet
from bu_cascade.assets.data_definition import DataDefinition
from bu_cascade.asset_tools import *

from tinker import cascade_connector
from tinker import app
from tinker import sentry
from tinker import cascade_connector

from BeautifulSoup import BeautifulStoneSoup


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == app.config['CASCADE_LOGIN']['username'] and password == app.config['CASCADE_LOGIN']['password']


def should_be_able_to_edit_image(roles):
    if 'FACULTY-CAS' in roles or 'FACULTY-BSSP' in roles or 'FACULTY-BSSD' in roles:
        return False
    else:
        return True


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


# def can_user_access_asset( username, id, type):
#     try:
#         user = read(username, "user")
#         allowed_groups = user.asset.user.groups
#     except AttributeError:
#        allowed_groups = ""
#     user_groups = allowed_groups.split(";")
#
#     response = read_access_rights(id, type)['accessRightsInformation']['aclEntries']['aclEntry']
#     response = [right['name'] for right in response]
#
#     if username in response or set(user_groups).intersection(set(response)):
#         return True
#     else:
#         return False


class TinkerController(object):
    def __init__(self):
        self.cascade_connector = cascade_connector
        self.datetime_format = "%B %d  %Y, %I:%M %p"

    def before_request(self):

        def init_user():

            dev = current_app.config['ENVIRON'] != 'prod'

            # if not production, then clear our session variables on each call
            if dev:
                for key in ['username', 'groups', 'roles', 'top_nav', 'user_email', 'name']:
                    if key in session.keys():
                        session.pop(key, None)

            if 'username' not in session.keys():
                get_user()

            if 'groups' not in session.keys():
                get_groups_for_user()

            if 'roles' not in session.keys():
                get_roles()

            if 'top_nav' not in session.keys():
                get_nav()

            if 'user_email' not in session.keys():
                # todo, get prefered email (alias) from wsapi once its added
                session['user_email'] = session['username'] + "@bethel.edu"

            if 'name' not in session.keys():
                get_users_name()

        def get_groups_for_user(username=None):

            if not username:
                username = session['username']
            try:
                user = self.read(username, "user")
                allowed_groups = find(user, 'groups', False)
            except AttributeError:
                allowed_groups = ""
            session['groups'] = allowed_groups

            return allowed_groups.split(";")

        def get_user():
            if current_app.config['ENVIRON'] == 'prod':
                username = request.environ.get('REMOTE_USER')
            else:
                username = current_app.config['TEST_USER']

            session['username'] = username

        def get_users_name(username=None):
            if not username:
                username = session['username']
            url = current_app.config['API_URL'] + "/username/%s/names" % username
            r = requests.get(url)
            names = fjson.loads(r.content)['0']
            if names['prefFirstName']:
                fname = names['prefFirstName']
            else:
                fname = names['firstName']
            lname = names['lastName']

            session['name'] = "%s %s" % (fname, lname)

        def get_roles(username=None):
            if not username:
                username = session['username']
            url = current_app.config['API_URL'] + "/username/%s/roles" % username
            r = requests.get(url, auth=(current_app.config['API_USERNAME'], current_app.config['API_PASSWORD']))
            roles = fjson.loads(r.content)
            ret = []
            for key in roles.keys():
                ret.append(roles[key]['userRole'])

            session['roles'] = ret

            return ret

        def get_nav():
            html = render_template('nav.html', **locals())
            session['top_nav'] = html

        init_user()
        get_nav()

    def clear_image_cache(self, image_path):
        # /academics/faculty/images/lundberg-kelsey.jpg"
        # Make sure image path starts with a slash
        if not image_path.startswith('/'):
            image_path = '/%s' % image_path

        resp = []

        for prefix in ['http://www.bethel.edu', 'https://www.bethel.edu',
                       'http://staging.bethel.edu', 'https://staging.bethel.edu']:
            path = prefix + image_path
            digest = hashlib.sha1(path.encode('utf-8')).hexdigest()
            path = "%s/%s/%s" % (app.config['THUMBOR_STORAGE_LOCATION'].rstrip('/'), digest[:2], digest[2:])
            resp.append(path)
            # remove the file at the path
            # if config.ENVIRON == "prod":
            call(['rm', path])

        # now the result storage
        file_name = image_path.split('/')[-1]
        matches = []
        for root, dirnames, filenames in os.walk(app.config['THUMBOR_RESULT_STORAGE_LOCATION']):
            for filename in fnmatch.filter(filenames, file_name):
                matches.append(os.path.join(root, filename))
        for match in matches:
            call(['rm', match])

        matches.extend(resp)

        return str(matches)

    # alphabetical order from here post before request/__init__

    def add_workflow_to_asset(self, workflow, data):
        data['workflowConfiguration'] = workflow

    def asset_in_workflow(self, asset_id, asset_type="page"):
        return self.cascade_connector.is_in_workflow(asset_id, asset_type=asset_type)

    def convert_month_num_to_name(self, month_num):
        return datetime.datetime.strptime(month_num, "%m").strftime("%B").lower()

    def copy(self, old_asset_path, new_path_and_name, asset_type):
        old_asset = ''
        # add a slash in front of path if it doesn't already have one
        if new_path_and_name[0] != "/":
            new_path_and_name = "/%s" % new_path_and_name

        old_asset = self.read(new_path_and_name, asset_type)

        if old_asset['success'] == 'false':
            # gather parent path and name
            array = new_path_and_name.rsplit("/", 1)
            parent_path = array[0]
            name = array[1]
            response = self.cascade_connector.copy(old_asset_path, asset_type, parent_path, name)
            app.logger.debug(time.strftime("%c") + ": Copy folder creation by " + session[
                'username'] + " From: " + old_asset_path + " To:" + new_path_and_name + str(response))
            return response
        return old_asset

    def create_block(self, asset):
        b = Block(self.cascade_connector, asset=asset)
        return b

    def create_page(self, asset):
        p = Page(self.cascade_connector, asset=asset)
        return p

    def create_workflow(self, workflow_id, subtitle=None):
        if not workflow_id:
            return None
        asset = self.read(workflow_id, 'workflowdefinition')

        workflow_name = find(asset, 'name', False)
        if subtitle:
            workflow_name += ": " + subtitle

        workflow = {
            "workflowName": workflow_name,
            "workflowDefinitionId": workflow_id,
            "workflowComments": workflow_name
        }
        return workflow

    def delete(self, path_or_id):
        return self.cascade_connector.delete(path_or_id)

    def element_tree_to_html(self, node):
        return_string = ''
        for child in node:
            child_text = ''
            if child.text:
                child_text = child.text

            # recursively renders children
            try:
                if child.tag == 'a':
                    return_string += '<%s href="%s">%s%s</%s>' % (
                        child.tag, child.attrib['href'], child_text, self.element_tree_to_html(child), child.tag)
                else:
                    return_string += '<%s>%s%s</%s>' % (
                        child.tag, child_text, self.element_tree_to_html(child), child.tag)
            except:
                # gets the basic text
                if child_text:
                    if child.tag == 'a':
                        return_string += '<%s href="%s">%s</%s>' % (
                            child.tag, child.attrib['href'], child_text, child.tag)
                    else:
                        return_string += '<%s>%s</%s>' % (child.tag, child_text, child.tag)

            # gets the text that follows the children
            if child.tail:
                return_string += child.tail

        return return_string

    # to be used to escape content to give to Cascade
    # Excape content so its Cascade WYSIWYG friendly
    def escape_wysiwyg_content(self, content):
        if content:
            uni = self.__html_entities_to_unicode__(content)
            htmlent = self.__unicode_to_html_entities__(uni)
            return htmlent
        else:
            return None

    def get_add_data(self, lists, form, wysiwyg_keys=[]):
        # A dict to populate with all the interesting data.
        add_data = {}

        for key in form.keys():
            if key in lists:
                add_data[key] = form.getlist(key)
            else:
                if key in wysiwyg_keys:
                    add_data[key] = self.escape_wysiwyg_content(form[key])
                else:
                    add_data[key] = form[key]

        # Create the system-name from title, all lowercase, remove any non a-z, A-Z, 0-9
        system_name = add_data['title'].lower().replace(' ', '-')
        add_data['system_name'] = re.sub(r'[^a-zA-Z0-9-]', '', system_name)

        # add author
        add_data['author'] = session['username']

    def edit_all(self, type_to_find, xml_url):
        assets_to_edit = self.traverse_xml(xml_url, type_to_find)
        for page_values in assets_to_edit:
            id = page_values['id']
            if type_to_find == 'system-page':
                asset = self.read_page(id)
            elif type_to_find == 'system-block':
                asset = self.read_block(id)
            else:
                continue

            asset_data, mdata, sdata = asset.get_asset()
            self.edit_all_callback(asset_data)
            asset.edit_asset(asset_data)
            asset.publish_asset()

    def edit_all_callback(self, asset_data):
        pass

    def get_edit_data(self, sdata, mdata, multiple=[]):
        """ Takes in data from a Cascade connector 'read' and turns into a dict of key:value pairs for a form."""
        edit_data = {}

        for m in multiple:
            edit_data[m] = []

        for node in find(sdata, 'identifier'):
            if node['identifier'] in multiple:
                m = node['identifier']
                edit_data[m].append(self.inspect_sdata_node(node))

            else:
                node_identifier = node['identifier'].replace('-', '_')
                edit_data[node_identifier] = self.inspect_sdata_node(node)

        dynamic_fields = find(mdata, 'fieldValues')
        # now metadata dynamic fields
        for field in dynamic_fields:
            if find(field, 'fieldValue'):
                items = [find(item, 'value') for item in find(field, 'fieldValue')]
                edit_data[field['name'].replace('-', '_')] = items

        # Add the rest of the fields. Can't loop over these kinds of metadata
        edit_data['title'] = mdata['title']
        edit_data['metaDescription'] = mdata['metaDescription']

        # get the (first) author
        authors = find(mdata, 'author', False)
        try:
            authors = authors.split(", ")
            edit_data['author'] = authors[0]
        except AttributeError:
            edit_data['author'] = ''

        return edit_data

    def group_callback(self, node):
        pass

    def __html_entities_to_unicode__(self, text):
        """Converts HTML entities to unicode.  For example '&amp;' becomes '&'."""
        text = unicode(BeautifulStoneSoup(text, convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
        return text

    def inspect_child(self, child):
        # interface method
        pass

    def inspect_sdata_node(self, node):

        node_type = node['type']

        if node_type == 'group':
            group = {}
            for n in node['structuredDataNodes']['structuredDataNode']:
                node_identifier = n['identifier'].replace('-', '_')
                group[node_identifier] = self.inspect_sdata_node(n)
            return group

        elif node_type == 'text':
            has_text = 'text' in node.keys() and node['text']
            if not has_text:
                return
            try:
                date = datetime.datetime.strptime(node['text'], '%m-%d-%Y')
                if not date:
                    date = ''
                return date
            except ValueError:
                pass

            try:
                if len(node['text']) >= 9:
                    date = self.__unicode_to_html_entities__(node['text'])
                    if not date:
                        date = ''
                    return date
            except TypeError:
                pass
            except ValueError:
                pass

            # A fix to remove the &#160; character from appearing (non-breaking whitespace)
            # Cascade includes this, for whatever reason.
            return node['text'].replace('&amp;#160;', ' ')

        elif node_type == 'asset':
            asset_type = node['assetType']
            if asset_type == 'file':
                if 'filePath' in node:
                    return node['filePath']
                else:
                    return ''

    def get_add_data(self, lists, form, wysiwyg_keys=[]):
        # A dict to populate with all the interesting data.
        add_data = {}

        for key in form.keys():
            if key in lists:
                add_data[key] = form.getlist(key)
            else:
                if key in wysiwyg_keys:
                    add_data[key] = self.escape_wysiwyg_content(form[key])
                else:
                    add_data[key] = form[key]

        if 'title' in add_data:
            title = add_data['title']
        elif 'first' in add_data and 'last' in add_data:
            title = add_data['first'] + ' ' + add_data['last']
        else:
            title = None

        if title:
            add_data['title'] = title

            # Create the system-name from title, all lowercase, remove any non a-z, A-Z, 0-9
            system_name = title.lower().replace(' ', '-')
            add_data['system_name'] = re.sub(r'[^a-zA-Z0-9-]', '', system_name)
            add_data['name'] = add_data['system_name']

        # add author
        add_data['author'] = session['username']

        return add_data

    def log_sentry(self, message, response):

        username = session['username']
        log_time = time.strftime("%c")
        response = str(response)

        sentry.client.extra_context({
            'Time': log_time,
            'Author': username,
            'Response': response
        })

        # log generic message to Sentry for counting
        app.logger.info(message)
        # more detailed message to debug text log
        app.logger.debug("%s: %s: %s %s" % (log_time, message, username, response))

    def move(self, page_id, destination_path, type='page'):
        return self.cascade_connector.move(page_id, destination_path, type)

    def publish(self, path_or_id, asset_type='page', destination='production'):
        return self.cascade_connector.publish(path_or_id, asset_type, destination)

    def read(self, path_or_id, type):
        return self.cascade_connector.read(path_or_id, type)

    def read_block(self, path_or_id):
        b = Block(self.cascade_connector, path_or_id)
        return b

    def read_datadefinition(self, path_or_id):
        dd = DataDefinition(self.cascade_connector, path_or_id)
        return dd

    def read_metadata_set(self, path_or_id):
        ms = MetadataSet(self.cascade_connector, path_or_id)
        return ms

    def read_page(self, path_or_id):
        p = Page(self.cascade_connector, path_or_id)
        p.read_asset()
        return p

    def rename(self):
        pass

    def traverse_xml(self, xml_url, type_to_find):

        response = urllib2.urlopen(xml_url)
        form_xml = ET.fromstring(response.read())

        matches = []
        for child in form_xml.findall('.//' + type_to_find):
            match = self.inspect_child(child)
            if match:
                matches.append(match)

        # Todo: maybe add some parameter as a search?
        # sort by created-on date.
        matches = sorted(matches, key=lambda k: k['created-on'])

        return matches

    def __unicode_to_html_entities__(self, text):
        """Converts unicode to HTML entities.  For example '&' becomes '&amp;'."""
        text = cgi.escape(text).encode('ascii', 'xmlcharrefreplace')
        return text

    def unpublish(self, path_or_id, asset_type):
        return self.cascade_connector.unpublish(path_or_id, asset_type)

    def update_asset(self, asset, data):
        for key, value in data.iteritems():
            if key == 'exceptions':
                print 'TEST'
            update(asset, key, value)

        return True

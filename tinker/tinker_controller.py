# Global
import cgi
import datetime
import fnmatch
import hashlib
import inspect
import logging
import os
import re
import time
import warnings
from functools import wraps
from HTMLParser import HTMLParser
from subprocess import call
from xml.etree import ElementTree as ET

# Packages
import requests
# from __future__ import print_function # Python 2/3 compatibiltiy (namedentities) - this might not be needed anymore
from createsend import Client
from jinja2 import Environment, FileSystemLoader, meta
from bu_cascade.assets.block import Block
from bu_cascade.assets.data_definition import DataDefinition
from bu_cascade.assets.metadata_set import MetadataSet
from bu_cascade.assets.page import Page
from bu_cascade.asset_tools import find, update
from flask import abort, current_app, render_template, request, Response, session
from flask import json as fjson
from namedentities import numeric_entities  # (namedentities)
from paramiko import RSAKey, SFTPClient, Transport
from paramiko.hostkeys import HostKeyEntry
from requests.packages.urllib3.exceptions import SNIMissingWarning, InsecurePlatformWarning
from unidecode import unidecode
from werkzeug.datastructures import ImmutableMultiDict

# Local
from tinker import app, cascade_connector, sentry, cache


class EncodingDict(object):
    # This class was created because some of the unicode strings being passed to Cascade didn't properly encode to
    # ASCII/UTF-8, and that caused problems. Rather than go through the whole project and write the same code over
    # and over, I created this object to wrap request.form dictionaries and sanitize the values returned as they're
    # requested via dictionary key lookups.
    def __init__(self, dictionary):
        self._failure = False
        if isinstance(dictionary, (ImmutableMultiDict, dict)):
            self._dictionary = dictionary
        else:
            self._failure = "EncodingDict was not passed an ImmutableMultiDict or dictionary"

    # This method allows us to use the rform['key'] shortcut
    def __getitem__(self, key):
        return self.get(key)

    # This method is written so that if we choose to, we can encode entire objects being returned by the dictionaries
    # instead of just the unicode strings.
    def _recursively_encode(self, item):
        if isinstance(item, dict):
            for key in item.keys():
                item[key] = self._recursively_encode(item[key])
            return item
        elif isinstance(item, ImmutableMultiDict):
            to_return = {}
            for key in item.keys():
                to_return[key] = self._recursively_encode(item[key])
            return ImmutableMultiDict(to_return)
        elif isinstance(item, list):
            return [self._recursively_encode(x) for x in item]
        elif isinstance(item, tuple):
            return (self._recursively_encode(x) for x in item)
        elif isinstance(item, unicode):
            return self._safely_encode_unicode_to_str(item)
        elif isinstance(item, (str, bool, int, long, float)) or item is None:
            # All of these types of objects don't need to be encoded from unicode to String, so they can pass through.
            return item
        else:
            # Anything else is unhandled
            return 'EncodingDict failed to encode object type %s' % type(item)

    # This method is what actually does the conversion from unicode to String
    def _safely_encode_unicode_to_str(self, unsafe_unicode):
        encoded_str = unidecode(unsafe_unicode)
        # numeric_entities | https://pypi.python.org/pypi/namedentities/1.9.4
        str_numeric_entities = numeric_entities(encoded_str)
        ampersand_hotfix = str_numeric_entities.replace('&', '&amp;')
        return ampersand_hotfix

    # This method returns the dictionary being wrapped by this object (used in WTForm Validation; they seem to need an
    # ImmutableMultiDict)
    def internal_dictionary(self):
        return self._dictionary

    # This is the primary wrapping method; it asks for the value at its internal dictionary's key, and if it returns a
    # unicode string, this method converts it to a String using the "correct" way.
    def get(self, key, default_return=None):
        if isinstance(self._failure, bool) and not self._failure:
            internal_get = self._dictionary.get(key, default_return)
            # return self._recursively_encode(internal_get)
            if isinstance(internal_get, unicode):
                internal_get = self._safely_encode_unicode_to_str(internal_get)
            return internal_get
        else:
            return self._failure

    # This method is written for ImmutableMultiDicts; they store data as a dictionary of dictionaries, allowing it to
    # accept multiple values for a single key (think of an HTML MultipleSelect; returns many values to one id). Since we
    # use this method in our code, I must "ape" the method and pass it on.
    def getlist(self, key):
        if isinstance(self._failure, bool) and not self._failure:
            if isinstance(self._dictionary, ImmutableMultiDict):
                internal_list_response = self._dictionary.getlist(key)
                # return self._recursively_encode(internal_list_response)
                to_return = []
                for item in internal_list_response:
                    if isinstance(item, unicode):
                        to_return.append(self._safely_encode_unicode_to_str(item))
                    else:
                        to_return.append(item)
                return to_return
            else:
                return "This EncodingDict does not have an ImmutableMultiDict stored internally, " \
                       "so getlist is not a valid method to call."
        else:
            return self._failure

    # Simple pass-along method
    def keys(self):
        if isinstance(self._failure, bool) and not self._failure:
            return self._dictionary.keys()
        else:
            return self._failure


class EncodingDictFactory(object):
    def encode(self, dictionary_to_encode):
        return EncodingDict(dictionary_to_encode)


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == app.config['CASCADE_LOGIN']['username'] and password == app.config['CASCADE_LOGIN']['password']


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


# checks the route base and uses the corresponding permissions to load the correct admin menu
def admin_permissions(flask_view_class):
    # program search menu
    if flask_view_class.route_base == '/admin/program-search':
        # give access to admins and lauren
        if 'Administrators' not in session['groups'] and 'parlau' not in session['groups'] and session['username'] != 'kaj66635':
            abort(403)

    # redirect menu
    elif flask_view_class.route_base == '/admin/redirect':
        # This if statement has to come first so that public API request don't need to have groups associated with them.
        if '/public/' in request.path:
            return

        # Checks to see what group the user is in
        if 'Administrators' not in session['groups'] and 'Tinker Redirects' not in session['groups']:
            abort(403)

    elif flask_view_class.route_base == '/admin/sync':
        # This if statement has to come first so that public API request don't need to have groups associated with them.
        if '/public/' in request.path:
            return

        # Checks to see what group the user is in
        if 'Administrators' not in session['groups']:
            abort(403)

    # all other admin menus
    elif 'Administrators' not in session['groups']:
        abort(403)


class TinkerController(object):
    def __init__(self):
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        # These two lines are to suppress warnings that only occur in 2.6.9; they are unnecessary in 2.7+
        requests.packages.urllib3.disable_warnings(SNIMissingWarning)
        requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
        self.datetime_format = "%B %d %Y, %I:%M %p"
        self.cascade_connector = cascade_connector
        self.dictionary_encoder = EncodingDictFactory()

    def before_request(self):
        def init_user():
            dev = current_app.config['ENVIRON'] != 'prod'

            # reset session if it has been more than 24 hours
            if 'session_time' in session.keys():
                seconds_in_day = 60 * 60 * 24
                day_is_passed = time.time() - session['session_time'] >= seconds_in_day
            else:
                day_is_passed = True
                session['session_time'] = time.time()

            # if not production, then clear our session variables on each call
            if (not session.get('admin_viewer', False)) and (dev or day_is_passed):
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

            if 'user_email' not in session.keys() and session['username']:
                # todo, get preferred email (alias) from wsapi once its added.
                session['user_email'] = session['username'] + "@bethel.edu"

            if 'name' not in session.keys() and session['username']:
                get_users_name()

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
            r = self.tinker_requests(url)
            try:
                # In some cases, '0' will not be a valid key, throwing a KeyError
                # If that happens, session['name'] should be an empty string so that checks in other locations will fail
                names = fjson.loads(r.content)['0']
                if names['prefFirstName']:
                    fname = names['prefFirstName']
                else:
                    fname = names['firstName']
                lname = names['lastName']
                session['name'] = "%s %s" % (fname, lname)
            except KeyError:
                session['name'] = ""

        def get_groups_for_user(username=None):
            skip = request.environ.get('skip-groups') == 'skip'

            if current_app.config['ENVIRON'] == 'prod':
                if not username:
                    username = session['username']
                if not skip:
                    try:
                        user = self.read(username, "user")
                        allowed_groups = find(user, 'groups', False)
                    except:
                        allowed_groups = ""
                else:
                    allowed_groups = ""
                if allowed_groups is None:
                    allowed_groups = ""
            else:
                allowed_groups = app.config['TEST_GROUPS']
            # print allowed_groups
            session['groups'] = allowed_groups
            return allowed_groups.split(";")

        def get_roles(username=None):
            if not username:
                username = session['username']
            url = current_app.config['API_URL'] + "/username/%s/roles" % username
            r = self.tinker_requests(url, auth=(current_app.config['API_USERNAME'], current_app.config['API_PASSWORD']))
            roles = fjson.loads(r.content)
            ret = []
            for key in roles.keys():
                ret.append(roles[key]['userRole'])

            session['roles'] = ret

            return ret

        def get_nav():
            html = render_template('nav.html', **locals())
            session['top_nav'] = html

        if '/public/' not in request.path and '/api/' not in request.path:
            init_user()
            get_nav()
        else:
            session['username'] = 'tinker'
            session['groups'] = []
            session['roles'] = []

    def cascade_call_logger(self, kwargs):
        # To use this, simply call:
        #     self.cascade_call_logger(locals())
        # right before the return statement of methods that make Cascade calls
        file_ = 'tinker/' + inspect.stack()[1][1].split('tinker/')[1]
        method = inspect.stack()[1][3]
        if 'self' in kwargs.keys():
            del kwargs['self']
        resp = {
            'file': file_,
            'method': method,
            'kwargs': kwargs
        }
        self.log_sentry("Cascade call", resp)

    def log_sentry(self, message, response):

        if app.config['UNIT_TESTING']:
            # Don't want to print out these log messages while unit testing
            return

        username = session['username']
        log_time = time.strftime("%c")
        response = str(response)

        sentry.client.extra_context({
            'Time': log_time,
            'Author': username,
            'Response': response
        })

        # log generic message to Sentry for counting
        # app.logger.info(message)
        sentry.captureMessage(message, level=logging.INFO)
        # more detailed message to debug text log
        app.logger.debug("%s: %s: %s %s" % (log_time, message, username, response))

    def inspect_child(self, child, find_all, csv):
        # interface method
        pass

    def traverse_xml(self, xml_url, type_to_find, find_all=False, csv=False):
        username = session['username']

        # Username is used for caching purposes
        @cache.memoize(timeout=300)
        def traverse_xml_cache(cache_username, cache_xml_url, cache_type_to_find, cache_find_all, cache_csv):
            response = self.tinker_requests(cache_xml_url)
            form_xml = ET.fromstring(response.content)

            matches = []

            for child in form_xml.findall('.//' + cache_type_to_find):
                match = self.inspect_child(child, cache_find_all, cache_csv)
                if match:
                    matches.append(match)

            # Todo: maybe add some parameter as a search?
            # sort by created-on date unless we are exporting csv, then sort by last name
            if cache_csv:
                matches = sorted(matches, key=lambda k: k['last'])
            else:
                matches = sorted(matches, key=lambda k: k['created-on'])

            return matches

        return traverse_xml_cache(username, xml_url, type_to_find, find_all, csv)

    # this function is necessary because we don't have python2.7 on the server (we use python2.6)
    def search_for_key_in_dynamic_md(self, block, key_to_find):
        return_values = []
        metadata = block.findall("dynamic-metadata")
        for md in metadata:
            if md.find('name').text == key_to_find:
                if hasattr(md.find('value'), 'text'):
                    return_values.append(md.find('value').text)
        return return_values

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

        dynamic_fields = find(mdata, 'dynamicField', False)
        # now metadata dynamic fields
        for field in dynamic_fields:
            if find(field, 'fieldValue', False):
                # find(item, 'value', False) was set in order for events md select fields to work
                items = [find(item, 'value', False) for item in find(field, 'fieldValue', False)]
                edit_data[field['name'].replace('-', '_')] = items

        # Add the rest of the fields. Can't loop over these kinds of metadata
        if 'title' in mdata:
            edit_data['title'] = mdata['title']
        if 'metaDescription' in mdata:
            edit_data['metaDescription'] = mdata['metaDescription']

        # get the authors
        edit_data['author'] = find(mdata, 'author', False)

        return edit_data

    def date_to_java_unix(self, date, datetime_format=None):

        if not datetime_format:
            datetime_format = self.datetime_format

        date = datetime.datetime.strptime(date, datetime_format)

        # if this is a time field with no date, the  year  will be 1900, and strftime("%s") will return -1000
        if date.year == 1900:
            date = date.replace(year=datetime.date.today().year)

        return int(date.strftime("%s")) * 1000

    def java_unix_to_date(self, date, date_format=None):
        if not date_format:
            date_format = self.datetime_format
        return datetime.datetime.fromtimestamp(int(date) / 1000).strftime(date_format)

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
                    date = self.java_unix_to_date(node['text'])
                    if not date:
                        date = ''
                    return date
            except TypeError:
                pass
            except ValueError:
                pass

            # A fix to remove the &#160; character from appearing (non-breaking whitespace)
            # Cascade includes this, for whatever reason.

            if '::CONTENT-XML-SELECTOR::' in node['text']:
                return node['text'].split('::CONTENT-XML-SELECTOR::')
            return node['text'].replace('&amp;#160;', ' ')

        elif node_type == 'asset':
            asset_type = node['assetType']
            if asset_type == 'file':
                if 'filePath' in node:
                    return node['filePath']
                else:
                    return ''

    def get_add_data(self, lists, form):
        # A dict to populate with all the interesting data.
        add_data = {}

        for key in form.keys():
            if key in lists:
                add_data[key] = form.getlist(key)
            else:
                add_data[key] = form[key]

        if 'title' in add_data:
            # strip() is called on the title to eliminate whitespace before and after the title
            title = add_data['title'].strip()
        elif 'first' in add_data and 'last' in add_data:
            # strip() is called on the title to eliminate whitespace before and after the title
            title = add_data['first'].strip() + ' ' + add_data['last'].strip()
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

    def create_block(self, asset):
        b = Block(self.cascade_connector, asset=asset)
        # TODO: maybe add cascade logger here? would like it in Block.init, but that's in bu_cascade
        return b

    def create_page(self, asset):
        p = Page(self.cascade_connector, asset=asset)
        # TODO: similarly, i'd like this to be logged by cascade_call_logger
        return p

    def read(self, path_or_id, type):
        return self.cascade_connector.read(path_or_id, type)

    def read_block(self, path_or_id):
        b = Block(self.cascade_connector, path_or_id)
        return b

    def read_page(self, path_or_id):
        p = Page(self.cascade_connector, path_or_id)
        p.read_asset()
        return p

    def read_metadata_set(self, path_or_id):
        ms = MetadataSet(self.cascade_connector, path_or_id)
        return ms

    def read_datadefinition(self, path_or_id):
        dd = DataDefinition(self.cascade_connector, path_or_id)
        return dd

    def publish(self, path_or_id, asset_type='page', destination='production'):
        resp = self.cascade_connector.publish(path_or_id, asset_type, destination)
        self.cascade_call_logger(locals())
        return resp

    def unpublish(self, path_or_id, asset_type):
        resp = self.cascade_connector.unpublish(path_or_id, asset_type)
        self.cascade_call_logger(locals())
        return resp

    def move(self, page_id, destination_path, type='page'):
        resp = self.cascade_connector.move(page_id, destination_path, type)
        self.cascade_call_logger(locals())
        return resp

    def delete(self, path_or_id, asset_type):
        resp = self.cascade_connector.delete(path_or_id, asset_type)
        self.cascade_call_logger(locals())
        return resp

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

    def update_asset(self, asset, data):
        for key, value in data.iteritems():
            update(asset, key, value)

        return True

    def add_workflow_to_asset(self, workflow, data):
        if not app.config.get('UNIT_TESTING'):
            data['workflowConfiguration'] = workflow

    def clear_image_cache(self, image_path):
        # /academics/faculty/images/lundberg-kelsey.jpg"
        # Make sure image path starts with a slash
        if not image_path.startswith('/'):
            image_path = '/%s' % image_path

        resp = []

        for prefix in ['http://www.bethel.edu', 'https://www.bethel.edu',
                       'http://staging.bethel.edu', 'https://staging.bethel.edu',
                       'http://thumbor.bethel.edu', 'https://thumbor.bethel.edu']:
            path = prefix + image_path
            digest = hashlib.sha1(path.encode('utf-8')).hexdigest()
            path = "%s/%s/%s" % (app.config['THUMBOR_STORAGE_LOCATION'].rstrip('/'), digest[:2], digest[2:])
            resp.append(path)
            # remove the file at the path
            # if config.ENVIRON == "prod":
            if not app.config['UNIT_TESTING']:
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

    def element_tree_to_html(self, node):
        return_string = ''
        for child in node:
            child_text = ''
            if child.text:
                child_text = child.text

            # recursively renders children
            try:
                if child.tag == 'a':
                    if hasattr(child, 'attrib') and 'href' in child.attrib:
                        child_href = child.attrib['href']
                    else:
                        child_href = '#'
                    return_string += '<%s href="%s">%s%s</%s>' % (
                        child.tag, child_href, child_text, self.element_tree_to_html(child), child.tag)
                else:
                    return_string += '<%s>%s%s</%s>' % (
                        child.tag, child_text, self.element_tree_to_html(child), child.tag)
            except:
                # gets the basic text
                if child_text:
                    if child.tag == 'a':
                        if hasattr(child, 'attrib') and 'href' in child.attrib:
                            child_href = child.attrib['href']
                        else:
                            child_href = '#'
                        return_string += '<%s href="%s">%s</%s>' % (
                            child.tag, child_href, child_text, child.tag)
                    else:
                        return_string += '<%s>%s</%s>' % (child.tag, child_text, child.tag)

            # gets the text that follows the children
            if child.tail:
                return_string += child.tail

        return return_string

    def search_cascade(self, search_information):
        return self.cascade_connector.search(search_information)

    def edit_all(self, type_to_find, xml_url):
        # assets_to_edit = self.traverse_xml(xml_url, type_to_find)
        # print len(assets_to_edit)
        # counter = 1
        # for page_values in assets_to_edit:
        #     id = page_values['id']
        #     print str(counter) + ' ' + id
        #     if type_to_find == 'system-page':
        #         asset = self.read_page(id)
        #     elif type_to_find == 'system-block':
        #         asset = self.read_block(id)
        #     else:
        #         continue
        #
        #     asset_data, mdata, sdata = asset.get_asset()
        #     self.edit_all_callback(asset_data)
        #     asset.edit_asset(asset_data)
        #     asset.publish_asset()
        #
        #     counter = counter + 1
        pass

    def edit_all_callback(self, asset_data):
        pass

    def list_relationships(self, path_or_id, asset_type):
        return self.cascade_connector.list_relationships(path_or_id, asset_type)

    def get_all_variables_from_jinja_template(self, relative_template_path):
        # Example template path: "faculty_bios/templates/faculty-bio-form.html"
        PATH = os.path.dirname(os.path.abspath(__file__))  # get the path of current file
        TEMPLATE_ENVIRONMENT = Environment(
            autoescape=False,
            loader=FileSystemLoader(os.path.join(PATH)),
            trim_blocks=False
        )
        template_source = TEMPLATE_ENVIRONMENT.loader.get_source(TEMPLATE_ENVIRONMENT, relative_template_path)[0]
        parsed_content = TEMPLATE_ENVIRONMENT.parse(template_source)
        variables = meta.find_undeclared_variables(parsed_content)
        keywords_to_ignore = set(['csrf_token', 'url_for'])
        return variables.difference(keywords_to_ignore)

    # # Not currently used in the code. However, this is helpful to find template IDs
    # def get_templates_for_client(self, campaign_monitor_key, client_id):
    #     for template in Client({'api_key': campaign_monitor_key}, client_id).templates():
    #         print template.TemplateID
    #
    # # Not currently used in the code. However, this is helpful to find segment IDs
    # def get_segments_for_client(self, campaign_monitor_key, client_id):
    #     for segment in Client({'api_key': campaign_monitor_key}, client_id).segments():
    #         print segment.SegmentID

    def convert_timestamps_to_bethel_string(self, open, close, all_day):
        try:
            is_all_day = False
            # If the event is all_day set it to true
            if all_day and all_day == 'Yes':
                is_all_day = True
            same_stamp = open == close

            # Format open and close
            proxy_open = datetime.datetime.fromtimestamp(open).strftime('%B %d, %Y, %-I:%M%p')
            proxy_close = datetime.datetime.fromtimestamp(close).strftime('%B %d, %Y, %-I:%M%p')

            same_day = datetime.datetime.fromtimestamp(open).strftime('%B %d, %Y') in proxy_close

            # If the event is all day, then the open string is formatted and close is set to an empty string
            all_day_format = 0
            if is_all_day:
                all_day_format = 1
                if same_day or same_stamp:
                    open = datetime.datetime.fromtimestamp(open).strftime('%B, %d, %Y')
                    close = ""
                else:
                    open = datetime.datetime.fromtimestamp(open).strftime('%B, %d')
                    close = datetime.datetime.fromtimestamp(close).strftime('%B, %d, %Y')

            elif same_day and not same_stamp:
                open = datetime.datetime.fromtimestamp(open).strftime('%B %d, %Y | %-I:%M%p')
                close = datetime.datetime.fromtimestamp(close).strftime('%-I:%M%p')
            elif same_stamp:
                open = datetime.datetime.fromtimestamp(open).strftime('%B %d, %Y | %-I:%M%p')
                close = ""
            else:
                open = proxy_open
                close = proxy_close

            bethel_date_string = self.final_format(open, close, all_day_format)
            return bethel_date_string
        except:
            return None

    def final_format(self, open, close, all_day_format):
        if close == "":
            combined_string = open
        else:
            if 'AM' in open and 'AM' in close and all_day_format == 1:
                open = open.replace("AM", "")
            elif 'PM' in open and 'PM' in close and all_day_format == 1:
                open = open.replace("PM", "")
            combined_string = "%s - %s" % (open, close)
        combined_string = combined_string.replace(':00', '')
        combined_string = combined_string.replace('AM', ' a.m.').replace('PM', ' p.m.')
        if '12 a.m.' in combined_string:
            combined_string = combined_string.replace('12 a.m.', 'at midnight')
        elif '12 p.m.' in combined_string:
            combined_string = combined_string.replace('12 p.m.', 'at noon')

        return combined_string

    def tinker_requests(self, url, auth=None, allow_redirects=True, verify=True):
        return requests.get(url, auth=auth, allow_redirects=allow_redirects, verify=verify,
                            headers={'Cache-Control': 'no-cache'})

    # Because of how SFTP is set up on wlp-fn2187, all these paths will be automatically prefixed with /var/www
    def write_redirects_to_sftp(self, from_path, to_path, cron):
        try:
            ssh_key_object = RSAKey(filename=app.config['SFTP_SSH_KEY_PATH'],
                                    password=app.config['SFTP_SSH_KEY_PASSPHRASE'])

            remote_server_public_key = HostKeyEntry.from_line(app.config['SFTP_REMOTE_HOST_PUBLIC_KEY']).key
            # This will throw a warning, but the (string, int) tuple will automatically be parsed into a Socket object
            remote_server = Transport((app.config['SFTP_REMOTE_HOST'], 22))
            remote_server.connect(hostkey=remote_server_public_key, username=app.config['SFTP_USERNAME'], pkey=ssh_key_object)

            sftp = SFTPClient.from_transport(remote_server)
            sftp.put(from_path, to_path)
            if cron:
                return 'SFTP publish from %s to %s succeeded' % (from_path, to_path)
            else:
                return fjson.dumps({
                    'type': 'success',
                    'message': 'Redirect updates successful'
                })
        except:
            if cron:
                return 'SFTP publish from %s to %s failed' % (from_path, to_path)
            else:
                return fjson.dumps({
                    'type': 'danger',
                    'message': 'Redirect updates failed'
                })

__author__ = 'ejc84332'

# python
import time
import hashlib
import os
import fnmatch
from subprocess import call
from functools import wraps

# flask
from flask import request
from flask import session
from flask import current_app
from flask import render_template
from flask import json as fjson
from flask import Response

import requests

# tinker
import config
from tinker import app
from tinker import sentry


def init_user():

    dev = current_app.config['ENVIRON'] != 'prod'

    # if dev:
    #     session.clear()

    if 'username' not in session.keys():
        get_user()

    if 'groups' not in session.keys():
        get_groups_for_user()

    if 'roles' not in session.keys():
        get_roles()

    if 'top_nav' not in session.keys():
        get_nav()

    if 'user_email' not in session.keys():
        # todo, get prefered email (alias) from wsapi once its added.
        session['user_email'] = session['username'] + "@bethel.edu"

    if 'name' not in session.keys():
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
    r = requests.get(url)
    names = fjson.loads(r.content)['0']
    if names['prefFirstName']:
        fname = names['prefFirstName']
    else:
        fname = names['firstName']
    lname = names['lastName']

    session['name'] = "%s %s" % (fname, lname)


def get_groups_for_user(username=None):
    from web_services import read
    if not username:
        username = session['username']
    try:
        user = read(username, "user")
        allowed_groups = user.asset.user.groups
    except AttributeError:
        allowed_groups = ""
    session['groups'] = allowed_groups

    return allowed_groups.split(";")


def get_roles(username=None):
    if not username:
        username = session['username']
    url = current_app.config['API_URL'] + "/username/%s/roles" % username
    r = requests.get(url, auth=(current_app.config['API_USERNAME'], current_app.config['API_PASSWORD']))
    roles = fjson.loads(r.content)
    ret = []
    for key in roles.keys():
        ret.append(roles[key]['userRole'])

    # Manually give 'faculty' privileges.
    # todo lets move this to a cascade group
    # if username == 'ejc84332':
    #    ret.append('FACULTY')
    # if username == 'ces55739':
    #     ret.append('FACULTY')
    if username == 'celanna':
        ret.append('FACULTY')

    session['roles'] = ret

    return ret


def get_nav():
    html = render_template('nav.html', **locals())
    session['top_nav'] = html


def log_sentry(message, response):

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


# does this go here?
def clear_image_cache(image_path):

    # /academics/faculty/images/lundberg-kelsey.jpg"
    # Make sure image path starts with a slash
    if not image_path.startswith('/'):
        image_path = '/%s' % image_path

    resp = []

    for prefix in ['http://www.bethel.edu', 'https://www.bethel.edu',
                   'http://staging.bethel.edu', 'https://staging.bethel.edu']:
        path = prefix + image_path
        digest = hashlib.sha1(path.encode('utf-8')).hexdigest()
        path = "%s/%s/%s" % (config.THUMBOR_STORAGE_LOCATION.rstrip('/'), digest[:2], digest[2:])
        resp.append(path)
        # remove the file at the path
        # if config.ENVIRON == "prod":
        call(['rm', path])

    # now the result storage
    file_name = image_path.split('/')[-1]
    matches = []
    for root, dirnames, filenames in os.walk(config.THUMBOR_RESULT_STORAGE_LOCATION):
        for filename in fnmatch.filter(filenames, file_name):
            matches.append(os.path.join(root, filename))
    for match in matches:
        call(['rm', match])

    matches.extend(resp)

    return str(matches)


def should_be_able_to_edit_image(roles):
    if 'FACULTY-CAS' in roles or 'FACULTY-BSSP' in roles or 'FACULTY-BSSD' in roles:
        return False
    else:
        return True


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

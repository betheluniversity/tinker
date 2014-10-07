__author__ = 'ejc84332'

from flask import request
from flask import session
from flask import current_app
from flask import g
from flask import render_template
from flask import json as fjson
import requests


def init_user():

    if 'username' not in session.keys():
        get_user()

    if 'groups' not in session.keys():
        get_groups_for_user()

    if 'roles' not in session.keys():
        get_roles()

    if 'top_nav' not in session.keys():
        get_nav()


def get_user():

    if current_app.config['ENVIRON'] == 'prod':
        username = request.environ.get('REMOTE_USER')
    else:
        username = current_app.config['TEST_USER']
    session['username'] = username
    g.user = username


def get_groups_for_user(username=None):
    from web_services import read
    if not username:
        username = session['username']
    user = read(username, "user")
    allowed_groups = user.asset.user.groups

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

    ## Manually give 'faculty' privileges.
    #todo lets move this to a cascade group
    #if username == 'ejc84332':
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


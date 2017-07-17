import requests
import time

from xml.etree import ElementTree as ET
from flask import render_template, session, request, make_response, redirect
from flask.ext.classy import FlaskView, route

from app import app

from datetime import datetime
# solution from here: https://stackoverflow.com/questions/1617078/ordereddict-for-older-versions-of-python
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

if __name__ == '__main__':
    class TinkerView(FlaskView):

        def __init__(self):
            # init is only run on server startup, so only xml can be loaded here
            xml = requests.get(app.config['XML_URL'])
            self.tabs = OrderedDict()
            self.blocks = {}
            self.icons = {}
            self.tab_title = ''
            self.load_tabs()
            self.load_blocks()

        def before_request(self, name, **kwargs):
            if app.config['DEBUG'] and not session.get('admin_viewer'):
                session.clear()

            start = datetime.now()
            if 'user_roles' not in session.keys():
                self.load_user_roles()
            if 'user_tabs' not in session.keys():
                self.load_user_tabs()
            if 'user_icons' not in session.keys():
                self.load_user_icons()

            if 'username' not in session.keys():
                if not app.config['DEBUG']:
                    session['username'] = request.environ.get('REMOTE_USER')
                elif not app.config['DEVELOPMENT']:
                    session['username'] = request.environ.get('REMOTE_USER')
                else:
                    session['username'] = app.config['TEST_USERNAME']

            start = datetime.now()
            if 'user_profile' not in session.keys():
                self.load_user_profile()
            end = datetime.now()
            print "load_user_profile: %s" % (end - start)

            url_tab = kwargs.get('tab', 'home')
            tab = url_tab.replace('-', ' ')
            # todo: sometimes flask is trying to load 'favicon.ico' as a Tab.
            # if not set(session['user_roles']).intersection(self.tabs[tab]['portal-roles']):
            #     return "not allowed"
            session['tab'] = tab
            session['url_tab'] = url_tab
            end = datetime.now()
            print "before_request: %s" % (end - start)

        def index(self):
            return self.get('home')

        def load_user_roles(self):
            if app.config['DEVELOPMENT']:
                session['user_roles'] = [role.upper() for role in app.config['ROLES']]
            else:
                session['user_roles'] = [role.upper() for roles in app.config['ROLES']]

        def 
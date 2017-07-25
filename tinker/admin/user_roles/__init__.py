import requests
import time

from xml.etree import ElementTree as ET
from flask import render_template, session, request, make_response, redirect, Blueprint
from flask_classy import FlaskView, route

from tinker import app
from tinker.tinker_controller import admin_permissions

from bu_cascade.cascade_connector import Cascade

from datetime import datetime
# solution from here: https://stackoverflow.com/questions/1617078/ordereddict-for-older-versions-of-python
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

UserRolesBlueprint = Blueprint('user_roles', __name__, template_folder='templates')


class UserRolesView(FlaskView):
    route_base = '/admin/user_roles'

    def __init__(self):
        pass

    def before_request(self, name, **kwargs):
        admin_permissions(self)

    def index(self):
        cascade_connection = Cascade(app.config['SOAP_URL'],
                                     {'username': app.config['CASCADE_LOGIN'].get('username'), 'password': app.config['CASCADE_LOGIN'].get('password')},
                                     app.config['SITE_ID'], app.config['STAGING_DESTINATION_ID'])
        role_asset = cascade_connection.read(app.config['CASCADE_MD_ROLES_ID'], 'metadataset')
        role_data = role_asset['asset']['metadataSet']['dynamicMetadataFieldDefinitions'][
            'dynamicMetadataFieldDefinition']

        cascade_md_roles = {}
        for item in role_data:
            try:
                cascade_md_roles[item['name']] = item['possibleValues']['possibleValue']
            except:
                continue
        return render_template('user_roles_home.html', **locals())

    def load_user_roles(self):
            if app.config['DEVELOPMENT']:
                session['user_roles'] = [role.upper() for role in app.config['ROLES']]
            else:
                session['user_roles'] = [role.upper() for role in app.config['ROLES']]

    @route('/test_roles_and_users_submit/', methods=['POST'])
    def test_roles_and_users_submit(self):
        if 'admin_username' in session.keys():
            current_username = session['admin_viewer_username']
        else:
            current_username = session['username']

        # get roles
        role = request.form.get('role')
        # get username
        username = request.form.get('username')

        # Todo: the main problem with doing role based checks, is some channels require a username
        if role:
            # set user_roles and clear user_tabs
            session['admin_viewer_role'] = role
            session['user_roles'] = [role]
        elif username:
            session.clear()
            session['admin_username'] = current_username
            session['username'] = username
        else:
            return 'error'

        session['admin_viewer'] = True
        return '/'  # have the JS handle where we go (homepage)

    @route('/test_roles_and_users_remove/')
    def test_roles_and_users_remove(self):
        session.clear()
        return 'success'

UserRolesView.register(UserRolesBlueprint)

import requests
import time

from xml.etree import ElementTree as ET
from flask import render_template, session, request, make_response, redirect, Blueprint
from flask_classy import FlaskView, route

from tinker import app
from tinker.tinker_controller import admin_permissions

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
        return render_template('index.html', **locals())

    def load_user_roles(self):
            if app.config['DEVELOPMENT']:
                session['user_roles'] = [role.upper() for role in app.config['ROLES']]
            else:
                session['user_roles'] = [role.upper() for role in app.config['ROLES']]

UserRolesView.register(UserRolesBlueprint)

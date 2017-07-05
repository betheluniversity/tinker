from flask import Blueprint, render_template
from flask_classy import FlaskView

from roles_roledata import uid, portal
from tinker.admin.admin_permissions import admin_permissions

BlinkRolesBlueprint = Blueprint('blink_roles', __name__, template_folder='templates')


class BlinkRolesView(FlaskView):
    route_base = '/admin/blink-roles'

    def before_request(self, args):
        admin_permissions('route_base', self, args)

    def index(self):
        uid_list = uid
        portal_list = portal
        return render_template('blink-roles-home.html', **locals())

BlinkRolesView.register(BlinkRolesBlueprint)

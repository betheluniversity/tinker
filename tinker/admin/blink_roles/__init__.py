from flask_classy import FlaskView
from flask import Blueprint, abort, session, render_template

# tinker
from roles_roledata import uid, portal

BlinkRolesBlueprint = Blueprint('blink-roles', __name__, template_folder='templates')


class BlinkRolesView(FlaskView):
    route_base = '/admin/blink-roles'

    def before_request(self, args):
        if 'Administrators' not in session['groups']:
            abort(403)

    def index(self):
        uid_list = uid
        portal_list = portal
        return render_template('blink-roles-home.html', **locals())

BlinkRolesView.register(BlinkRolesBlueprint)

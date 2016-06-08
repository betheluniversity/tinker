from flask.ext.classy import FlaskView
from flask import Blueprint, abort, session, render_template
from roles_roledata import uid, portal

roles_blueprint = Blueprint('roles', __name__, template_folder='templates')

class RolesView(FlaskView):

    # def __init__(self):
    #     self.base = RolesController

    def before_request(self):
        if 'Administrators' not in session['groups']:
            abort(403)

    def home(self):
        uid_list = uid
        portal_list = portal
        return render_template('blink-roles-home.html', **locals())

RolesView.register(roles_blueprint)

__author__ = 'ces55739'
from roles_roledata import uid, portal
# tinker
from flask import Blueprint, render_template, abort, session

blink_roles_blueprint = Blueprint('blink_roles_blueprint', __name__, template_folder='templates')


@blink_roles_blueprint.before_request
def before_request():
    if 'Administrators' not in session['groups']:
        abort(403)


@blink_roles_blueprint.route('/')
def home():
    uid_list = uid
    portal_list = portal
    return render_template('blink-roles-home.html', **locals())
__author__ = 'ces55739'
from roledata import uid, portal
# tinker
from flask import Blueprint, render_template

blink_roles_blueprint = Blueprint('blink_roles_blueprint', __name__, template_folder='templates')

@blink_roles_blueprint.route('/')
def home():
    uid_list = uid
    portal_list = portal
    return render_template('blink-roles-home.html', **locals())

"""@blink_roles_blueprint.route('/role/<uid>/<portal>')
def role_redirect():
    uid_list = uid
    portal_list = portal"""
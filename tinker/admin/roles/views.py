__author__ = 'ces55739'
from roles_roledata import uid, portal
# tinker
from flask import Blueprint, render_template

blink_roles_blueprint = Blueprint('blink_roles_blueprint', __name__, template_folder='templates')
from tinker.admin.views import admin_blueprint

@admin_blueprint.route('/sync')
def home():
    uid_list = uid
    portal_list = portal
    return render_template('blink-roles-home.html', **locals())
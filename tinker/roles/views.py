__author__ = 'ces55739'

# tinker
from flask import Blueprint, render_template

blink_roles_blueprint = Blueprint('blink_roles_blueprint', __name__, template_folder='templates')

@blink_roles_blueprint.route('/')
def home():
    return render_template('blink-roles-home.html', **locals())

# @blink_roles_blueprint.route('/')
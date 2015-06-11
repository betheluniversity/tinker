__author__ = 'ces55739'

# flask
from flask import Blueprint

# tinker
from tinker import app
from tinker.tools import *

publish_blueprint = Blueprint('publish', __name__, template_folder='templates')

@publish_blueprint.route("/")
def publish_home():
    username = session['username']
    # index page for adding events and things
    # return forms
    return render_template('publish-home.html', **locals())
#flask
from flask import render_template

from tinker.events.cascade_events import *
from tinker import app
from tinker import tools


@app.route('/')
def show_home():
    ## index page for adding events and things
    username = tools.get_user()
    forms = get_forms_for_user(username)
    return render_template('home.html', **locals())
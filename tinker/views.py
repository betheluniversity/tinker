#flask
from flask import render_template

import json

#flask



from tinker import app
from tinker import tools


@app.route('/')
def show_home():
    ## index page for adding events and things
    username = tools.get_user()

    return render_template('home.html', **locals())


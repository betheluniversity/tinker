#python
import json

#flask
from flask import render_template

#tinker
from tinker import tools
from tinker import app


@app.route('/')
def home():
    ## index page for adding events and things
    username = tools.get_user()

    return render_template('home.html', **locals())


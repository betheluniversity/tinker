#python
import json

#flask
from flask import render_template
from flask import request
from flask import send_file

#tinker
from tinker import tools
from tinker import app


@app.route('/')
def home():
    ## index page for adding events and things
    username = tools.get_user()

    return render_template('home.html', **locals())

@app.route('/get-image/<image_name>')
def get_image(image_name):
    return send_file('images/' + image_name, mimetype='image/png')

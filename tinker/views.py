#python
import json

#flask
from flask import render_template
from flask import json as fjson
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

@app.route('/about')
def about():
    return render_template('about-page.html', **locals())

@app.route('/get-image/<image_name>')
def get_image(image_name):
    return send_file('images/' + image_name, mimetype='image/png')



@app.route('/get-user-info', methods=['GET', 'POST'])
def get_user_info():

    #initialize user and roles
    username = tools.get_user()
    html = render_template('nav.html', **locals())
    return fjson.jsonify({'html': html})



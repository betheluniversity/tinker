# python


# flask
from flask import render_template
from flask import session
from flask import send_file

# tinker
from tinker import app


@app.route('/')
def home():
    # index page for adding events and things
    return render_template('home.html', **locals())


@app.route('/about')
def about():
    return render_template('about-page.html', **locals())


@app.route('/get-image/<image_name>')
def get_image(image_name):
    return send_file('images/' + image_name, mimetype='image/png')


@app.route('/test')
def test():
    session.clear()
    return "done"


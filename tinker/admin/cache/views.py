from flask import Blueprint, render_template, abort, session, request
from tinker import tools

cache_blueprint = Blueprint('cache_blueprint', __name__, template_folder='templates')

@cache_blueprint.before_request
def before_request():
    if 'Administrators' not in session['groups']:
        abort(403)

@cache_blueprint.route('/')
def home():
    return render_template('cache-home.html', **locals())

@cache_blueprint.route('/submit', methods=['post'])
def submit():
    path = request.form['url']
    return cache_clear(path)

def cache_clear(img_path=None):
    if not img_path:
        return "Please enter in a path."
    return tools.clear_image_cache(img_path)

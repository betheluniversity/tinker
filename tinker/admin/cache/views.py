from flask import Blueprint, render_template, abort, session

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
    return "success"
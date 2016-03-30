from flask import Blueprint, render_template, abort, session
cache_blueprint = Blueprint('cache_blueprint', __name__, template_folder='templates')

from flask import Flask, render_template, Blueprint, session, abort, request
from tinker import tools
from flask.ext.classy import FlaskView, route
from types import *

CacheBlueprint = Blueprint('CacheBlueprint', __name__, template_folder='templates')

class CacheClear(FlaskView):
    route_base = '/admin/cache-clear'

    def before_request(self, name, **kwargs):
        if 'Administrators' not in session['groups']:
            abort(403)

    def index(self):
        print "beginning of index method"
        return render_template('cache-home.html', **locals())

    def post(self):
        print "beginning of post method"
        # http://flask.pocoo.org/docs/0.11/patterns/jquery/ <--This is the tutorial I was following
        returnstring = request.args.get('url', "/", type=StringType)
        return returnstring
        path = request.form['url']
        return cache_clear(path)

def cache_clear(img_path=None):
    if not img_path:
        return "Please enter in a path."
    return tools.clear_image_cache(img_path)

CacheClear.register(CacheBlueprint)
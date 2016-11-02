# flask
from flask import Flask, render_template, Blueprint, session, abort, request
from flask_classy import FlaskView, route

# tinker
from tinker.admin.cache.cache_controller import CacheController

CacheBlueprint = Blueprint('cache', __name__, template_folder='templates')


class CacheView(FlaskView):
    route_base = '/admin/cache-clear'

    def __init__(self):
        self.base = CacheController()

    def before_request(self, name, **kwargs):
        if 'Administrators' not in session['groups']:
            abort(403)

    def index(self):
        return render_template('cache-home.html')

    # Todo: update the return of this to be creative-tim's notifications
    @route("/submit", methods=['post'])
    def submit(self):
        path = request.form['url']
        return self.base.cache_clear(path)

CacheView.register(CacheBlueprint)

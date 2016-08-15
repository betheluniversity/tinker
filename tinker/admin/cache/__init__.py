from flask import Flask, render_template, Blueprint, session, abort, request
from flask.ext.wtf import Form
from tinker import tools
from flask.ext.classy import FlaskView, route
from tinker.admin.cache.cache_controller import CacheController
CacheBlueprint = Blueprint('CacheBlueprint', __name__, template_folder='templates')


class CacheClear(FlaskView):
    route_base = '/admin/cache-clear'

    def __init__(self):
        self.base = CacheController()

    def before_request(self, name, **kwargs):
        if 'groups' not in session:
            # This if statement block has been added for unit testing purposes
            from tinker.tinker_controller import TinkerController
            tc = TinkerController()
            tc.before_request()
        if 'Administrators' not in session['groups']:
            abort(403)

    def index(self):
        # This form is defined solely for CSRF token validation
        form = Form()
        return render_template('cache-home.html', form=form)

    # Todo: update the return of this to be creative-tim's notifications
    @route("/submit", methods=['post'])
    def submit(self):
        path = request.form['url']
        return self.base.cache_clear(path)

CacheClear.register(CacheBlueprint)

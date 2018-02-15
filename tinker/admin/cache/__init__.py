# Packages
from flask import Blueprint, render_template, request
from flask_classy import FlaskView, route

# Local
from tinker.admin.cache.cache_controller import CacheController
from tinker.tinker_controller import admin_permissions
from tinker import cache

CacheBlueprint = Blueprint('cache', __name__, template_folder='templates')


class CacheView(FlaskView):
    route_base = '/admin/cache-clear'

    def __init__(self):
        self.base = CacheController()

    def before_request(self, name, **kwargs):
        admin_permissions(self)

    def index(self):
        return render_template('admin/cache/home.html')

    # Todo: update the return of this to be creative-tim's notifications
    @route("/submit", methods=['post'])
    def submit(self):
        rform = self.base.dictionary_encoder.encode(request.form)
        path = rform['url']
        return self.base.cache_clear(path)

CacheView.register(CacheBlueprint)

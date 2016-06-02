__author__ = 'ejc84332'

from flask import Blueprint, render_template

from flask.ext.classy import FlaskView

from tinker.new_redirects.redirects_controller import RedirectsController
from tinker.redirects.models import BethelRedirect

RedirectsBlueprint = Blueprint('redirects', __name__, template_folder='templates')

class RedirectsView(FlaskView):
    route_base = '/admin/redirect'

    def __init__(self):
        self.base = RedirectsController()

    def index(self):
        self.base.check_redirect_groups()
        redirects = BethelRedirect.query.all()

        return render_template('redirects.html', **locals())

RedirectsView.register(RedirectsBlueprint)
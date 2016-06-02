__author__ = 'ejc84332'

from flask import render_template

from flask.ext.classy import FlaskView

from tinker.new_redirects.redirects_controller import RedirectsController
from tinker.redirects.models import BethelRedirect


class RedirectsView(FlaskView):
    route_base = '/admin/redirect'

    def __init__(self):
        self.base = RedirectsController()

    def show(self):
        self.base.check_redirect_groups()
        redirects = BethelRedirect.query.all()

        return render_template('redirects.html', **locals())


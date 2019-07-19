# Global
import re

# Packages
import requests
from BeautifulSoup import BeautifulSoup
from bu_cascade.asset_tools import find
from flask import render_template, request, session, abort
from flask_classy import FlaskView, route

# Local
from tinker.admin.publish.publish_manager_controller import PublishManagerController
from tinker.tinker_controller import admin_permissions, requires_auth


class PublishView(FlaskView):
    route_base = '/admin/publish-manager'

    def __init__(self):
        self.base = PublishManagerController()

    # This method is called before any request to check user's credentials
    def before_request(self, name, **kwargs):
        if '/program-feeds/public/' not in request.url:
            admin_permissions(self)

    # Publish manager's homepage
    def index(self):
        username = session['username']
        return render_template('admin/publish/home.html', **locals())

    @route("/program-feeds")
    def publish_program_feeds(self):
        return render_template('admin/publish/program-feeds.html', **locals())

    # in puppet, we don't require CAS auth for this, so we can call it from cron and load it normally
    @requires_auth
    @route("/program-feeds/public/<destination>")
    def cron_publish_program_feeds_return(self, destination=''):
        return self.base.publish_program_feeds(destination)

    @route("/program-feeds/<destination>")
    def publish_program_feeds_return(self, destination=''):
        return self.base.publish_program_feeds(destination)


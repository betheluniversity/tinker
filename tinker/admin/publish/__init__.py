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
from tinker.tinker_controller import admin_permissions


class PublishView(FlaskView):
    route_base = '/admin/publish-manager'

    def __init__(self):
        self.base = PublishManagerController()

    # This method is called before any request to check user's credentials
    def before_request(self, name, **kwargs):
        admin_permissions(self)

    # Publish manager's homepage
    def index(self):
        username = session['username']
        return render_template('admin/publish/home.html', **locals())

    @route("/program-feeds")
    def publish_program_feeds(self):
        return render_template('admin/publish/program-feeds.html', **locals())

    @route("/program-feeds/<destination>")
    def publish_program_feeds_return(self, destination=''):
        if destination != "production":
            destination = "staging"

        # get results
        results = self.base.search_data_definitions("*program-feed*")
        if results.matches is None or results.matches == "":
            results = []
        else:
            results = results.matches.match

        final_results = []

        # publish all results' relationships
        for result in results:
            type = result.type
            id = result.id

            if type == "block" and '/base-assets/' not in result.path.path and '_testing/' not in result.path.path:
                try:
                    relationships = self.base.list_relationships(id, type)
                    pages = relationships.subscribers.assetIdentifier
                    pages_added = []
                    for page in pages:
                        resp = self.base.publish(page.id, "page", destination)
                        if 'success = "false"' in str(resp):
                            message = resp['message']
                        else:
                            message = 'Published'
                        pages_added.append({'id': page.id, 'path': page.path.path, 'message': message})
                except:
                    continue

                final_results.append({'id': result.id, 'path': result.path.path, 'pages': pages_added})

        return render_template('admin/publish/program-feeds-table.html', **locals())

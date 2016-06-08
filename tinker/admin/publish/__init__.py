import re
import urllib

from flask import Blueprint, render_template, request
from flask.ext.classy import FlaskView, route

from tinker.admin.publish.publish_manager_controller import PublishManagerController
from tinker.web_services import *

from BeautifulSoup import BeautifulSoup

PublishManagerBlueprint = Blueprint('publish-manager', __name__, template_folder='templates')


class PublishManagerView(FlaskView):
    route_base = '/admin/publish-manager'

    def __init__(self):
        self.base = PublishManagerController()

    def before_request(self, name, **kwargs):
        if 'Administrators' not in session['groups']:
            abort(403)

    def index(self):
        username = session['username']

        return render_template('publish-home.html', **locals())

    @route("/program-feeds", methods=['get', 'post'])
    def publish_program_feeds(self):
        return render_template('publish-program-feeds.html', **locals())

    @route("/program-feeds/<destination>", methods=['get', 'post'])
    def publish_program_feeds_return(self, destination=''):
        if destination != "production":
            destination = "staging"

        # get results
        results = search_data_definitions("*program-feed*")
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
                    relationships = list_relationships(id, type)
                    pages = relationships.subscribers.assetIdentifier
                    pages_added = []
                    for page in pages:
                        # TODO not sure if this should use self.base
                        resp = self.base.publish(page.id, "page", destination)
                        if 'success = "false"' in str(resp):
                            message = resp['message']
                        else:
                            message = 'Published'
                        pages_added.append({'id': page.id, 'path': page.path.path, 'message': message})
                except:
                    continue

                final_results.append({'id': result.id, 'path': result.path.path, 'pages': pages_added})

        return render_template('publish-program-feeds-table.html', **locals())

    @route('/search', methods=['get', 'post'])
    def search(self):
        name = request.form['name']
        content = request.form['content']
        metadata = request.form['metadata']

        # test search info
        results = self.base.search(name, content, metadata)
        if results.matches is None or results.matches == "":
            results = []
        else:
            results = results.matches.match

        final_results = []
        for result in results:
            if result.path.siteName == "Public" and (not re.match("_", result.path.path) or re.match("_shared-content", result.path.path) or re.match("_homepages", result.path.path)):
                final_results.append(result)

        results = final_results
        return render_template('publish-table.html', **locals())

    @route('/publish/<destination>/<type>/<id>', methods=['get', 'post'])
    def publish_publish(self, destination, type, id):
        if destination != "staging":
            destination = ""

        if type == "block":
            try:
                relationships = list_relationships(id, type)
                pages = relationships.subscribers.assetIdentifier
                for page in pages:
                    if page.type == "page":
                        # TODO not sure if this should use self.base
                        resp = self.base.publish(page.id, "page", destination)
                if 'success = "false"' in str(resp):
                    return resp['message']
            except:
                return "Failed"
        else:
            # TODO not sure if this should use self.base
            resp = self.base.publish(id, type, destination)
            if 'success = "false"' in str(resp):
                return resp['message']

        return "Publishing. . ."

    @route("/more_info", methods=['post'])
    def more_info(self):
        type = request.form['type']
        id = request.form['id']

        resp = read(id, type)

        # page
        if type == 'page':
            try:
                info = resp.asset.page
                md = info.metadata
                ext = 'php'
            except:
                return "Not a valid type. . ."
        # block
        elif type == 'block':
            try:
                info = resp.asset.xhtmlDataDefinitionBlock
                md = info.metadata
                ext = ""
            except:
                return "Not a valid type. . ."
        # Todo: file
        else:
            return "Not a valid type. . ."

        # name
        if info.name:
            name = info.name
        # title
        if md.title:
            title = md.title
        # path
        if info.path:
            path = info.path

            if ext != "":
                try:
                    www_publish_date = 'N/A'
                    staging_publish_date = 'N/A'
                    # prod
                    # www publish date
                    page3 = urllib.urlopen("https://www.bethel.edu/" + path + '.' + ext).read()
                    soup3 = BeautifulSoup(page3)
                    date = soup3.findAll(attrs={"name": "date"})
                    if date:
                        www_publish_date = self.base.convert_meta_date(date)

                    # staging
                    page3 = urllib.urlopen("https://staging.bethel.edu/" + path + '.' + ext).read()
                    soup3 = BeautifulSoup(page3)
                    date = soup3.findAll(attrs={"name": "date"})
                    if date:
                        staging_publish_date = self.base.convert_meta_date(date)

                except:
                    www_publish_date = 'N/A'
                    staging_publish_date = 'N/A'
        # description
        if md.metaDescription:
            description = md.metaDescription

        return render_template("publish-more-info.html", **locals())

PublishManagerView.register(PublishManagerBlueprint)

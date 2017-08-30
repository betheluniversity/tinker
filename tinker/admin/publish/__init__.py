# Global
import re

# Packages
import requests
from BeautifulSoup import BeautifulSoup
from bu_cascade.asset_tools import find
from flask import Blueprint, render_template, request, session
from flask_classy import FlaskView, route

# Local
from tinker.admin.publish.publish_manager_controller import PublishManagerController
from tinker.tinker_controller import admin_permissions

PublishBlueprint = Blueprint('publish', __name__, template_folder='templates')


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

    @route("/program-feeds", methods=['get', 'post'])
    def publish_program_feeds(self):
        return render_template('admin/publish/program-feeds.html', **locals())

    @route("/program-feeds/<destination>", methods=['get', 'post'])
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

    # Finds all pages, blocks, files, and folders dependent on the
    # name, content, or metadata entered by the user
    @route('/search', methods=['get', 'post'])
    def search(self):
        name = request.form['name']
        content = request.form['content']
        metadata = request.form['metadata']
        pages = request.form['pages']
        blocks = request.form['blocks']
        files = request.form['files']
        folders = request.form['folders']

        # test search info
        results = self.base.search(name, content, metadata, pages, blocks, files, folders)
        if results.matches is None or results.matches == "":
            results = []
        else:
            results = results.matches.match

        final_results = []
        for result in results:
            if result.path.siteName == "Public" and (not re.match("_", result.path.path) or re.match("_shared-content", result.path.path) or re.match("_homepages", result.path.path)):
                final_results.append(result)

        results = final_results
        return render_template('admin/publish/table.html', **locals())

    # Publishes the block or page that user
    @route('/publish/<destination>/<type>/<id>', methods=['get', 'post'])
    def publish_publish(self, destination, type, id):
        if destination != "staging":
            # Empty string destination will have it publish to all locations, not just staging
            destination = ""
        # todo create method for publishing blocks
        if type == "block":
            try:
                relationships = self.base.list_relationships(id, type)
                pages = relationships.subscribers.assetIdentifier
                for page in pages:
                    if page.type == "page":
                        resp = self.base.publish(page.id, "page", destination)
                if 'success = "false"' in str(resp):
                    return resp['message']
            except:
                return "Failed"
        else:
            resp = self.base.publish(id, type, destination)
            if 'success = "false"' in str(resp):
                return resp['message']
        return "Publishing. . ."

    # Displays info about the published block or page
    # Displays examples on web page
    @route("/more_info", methods=['post'])
    def more_info(self):
        info_type = request.form['type']
        info_id = request.form['id']

        # page
        if info_type == 'page':
            try:
                page = self.base.read_page(info_id)
                asset, mdata, sdata = page.read_asset()
                ext = 'php'
            except:
                return "Cannot find page."
        # block
        elif info_type == 'block':
            try:
                asset = self.base.read_block(info_id)
            except:
                return "Cannot find block."
        # Todo: file
        else:
            return "Not a valid type. . ."

        # name
        if asset:
            try:
                path = find(asset, 'path', False)
                title = find(asset, 'title', False)

                # prod
                www_publish_date = 'N/A'
                page3 = requests.get("https://www.bethel.edu/" + path + '.' + ext).content
                soup3 = BeautifulSoup(page3)
                date = soup3.findAll(attrs={"name": "date"})
                if date:
                    www_publish_date = self.base.convert_meta_date(date)

                # staging
                staging_publish_date = 'N/A'
                page3 = requests.get("https://staging.bethel.edu/" + path + '.' + ext).content
                soup3 = BeautifulSoup(page3)
                date = soup3.findAll(attrs={"name": "date"})
                if date:
                    staging_publish_date = self.base.convert_meta_date(date)

            except:
                www_publish_date = 'N/A'
                staging_publish_date = 'N/A'

        return render_template("admin/publish/more-info.html", **locals())

PublishView.register(PublishBlueprint)

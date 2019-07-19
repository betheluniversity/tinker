# Global
from datetime import datetime

# Packages
from flask import render_template

# Local
from tinker.tinker_controller import TinkerController


class PublishManagerController(TinkerController):

    def search_data_definitions(self, name_search=""):
        search_information = {
            'searchTerms': name_search,
            'searchTypes': {
                'searchType': ['block']
            },
            'searchFields': {
                'searchField': ['name']
            }
        }
        response = self.search_cascade(search_information)
        return response

    def publish_program_feeds(self, destination):
        if destination != "production":
            destination = "staging"

        # get results
        results = self.search_data_definitions("*program-feed*")
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
                    relationships = self.list_relationships(id, type)
                    pages = relationships.subscribers.assetIdentifier
                    pages_added = []
                    for page in pages:
                        resp = self.publish(page.id, "page", destination)
                        if 'success = "false"' in str(resp):
                            message = resp['message']
                        else:
                            message = 'Published'
                        pages_added.append({'id': page.id, 'path': page.path.path, 'message': message})
                except:
                    continue

                final_results.append({'id': result.id, 'path': result.path.path, 'pages': pages_added})

        return render_template('admin/publish/program-feeds-table.html', **locals())
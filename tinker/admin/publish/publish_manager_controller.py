# Global
from datetime import datetime

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
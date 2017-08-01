# Global
from datetime import datetime

# Local
from tinker.tinker_controller import TinkerController


class PublishManagerController(TinkerController):

    def convert_meta_date(self, date):
        dates = date[0]['content'].encode('utf-8').split(" ")
        dates.pop()
        date = " ".join(dates)

        dt = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S")
        date_time = dt.strftime("%B %e, %Y at %I:%M %p")

        return date_time

    def search(self, name_search="", content_search="", metadata_search="", pages_search="", blocks_search="",
               files_search="", folders_search=""):

        search_information = {
            'matchType': "match-all",
            'assetName': name_search,
            'assetContent': content_search,
            'assetMetadata': metadata_search,
            'searchPages': pages_search,
            'searchBlocks': blocks_search,
            'searchFiles': files_search,
            'searchFolders': folders_search,
        }

        response = self.search_cascade(search_information)
        return response

    def search_data_definitions(self, name_search=""):
        search_information = {
            'matchType': "match-all",
            'assetName': name_search,
            'searchBlocks': True,
        }
        response = self.search_cascade(search_information)
        return response

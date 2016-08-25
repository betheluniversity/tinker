from datetime import datetime
from suds.client import Client
from suds.transport import TransportError

# tinker
from tinker.tinker_controller import TinkerController
from tinker import app

# flask
from flask import abort


class PublishManagerController(TinkerController):

    def convert_meta_date(self, date):
        dates = date[0]['content'].encode('utf-8').split(" ")
        dates.pop()
        date = " ".join(dates)

        dt = datetime.strptime(date, "%a, %d %b %Y %H:%M:%S")
        date_time = datetime.strftime(dt, "%B %e, %Y at %I:%M %p")

        return date_time

    # todo these two methods must be removed eventually
    # todo all methods below are from web services.py
    def get_client(self):
        try:
            client = Client(url=app.config['WSDL_URL'], location=app.config['SOAP_URL'])
            return client
        except TransportError:
            abort(503)

    def search(self, name_search="", content_search="", metadata_search="", pages_search="", blocks_search="",
               files_search="", folders_search=""):
        client = self.get_client()

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

        auth = app.config['CASCADE_LOGIN']

        # todo
        response = client.service.search(auth, search_information)
        # app.logger.debug(time.strftime("%c") + ": Search " + str(response))

        return response

    def search_data_definitions(self, name_search=""):
        client = self.get_client()

        search_information = {
            'matchType': "match-all",
            'assetName': name_search,
            'searchBlocks': True,
        }

        auth = app.config['CASCADE_LOGIN']

        response = client.service.search(auth, search_information)

        return response

    def list_relationships(self, id, type="page"):
        auth = app.config['CASCADE_LOGIN']
        client = self.get_client()

        identifier = {
            'id': id,
            'type': type,
        }

        response = client.service.listSubscribers(auth, identifier)

        return response

from tinker.tinker_controller import TinkerController

from datetime import datetime

from tinker import app

from suds.client import Client
from suds.transport import TransportError

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
    def get_client(self):
        try:
            client = Client(url=app.config['WSDL_URL'], location=app.config['SOAP_URL'])
            return client
        except TransportError:
            abort(503)

    def search(self, name_search="", content_search="", metadata_search=""):
        client = self.get_client()

        search_information = {
            'matchType': "match-all",
            'assetName': name_search,
            'assetContent': content_search,
            'assetMetadata': metadata_search,
            'searchPages': True,
            'searchBlocks': False,
            'searchFiles': True,
            'searchFolders': True,
        }

        auth = app.config['CASCADE_LOGIN']

        # todo
        response = client.service.search(auth, search_information)
        # app.logger.debug(time.strftime("%c") + ": Search " + str(response))

        return response

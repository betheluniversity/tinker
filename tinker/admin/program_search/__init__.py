import urllib2
import gspread
from xml.etree import ElementTree as ET
from oauth2client.service_account import ServiceAccountCredentials


from tinker import app
from flask.ext.classy import FlaskView



class ProgramSearchView(FlaskView):

    def __init__(self):
        pass

    def index(self):
        return "program search index"

    def put(self, tag_id=None):
        return "put tag with id: %s" % tag_id

    def delete(self, tag_id=None):
        return "delete tag with id: %s" % tag_id

    def get(self, tag_id=None):
        return "get tag with id: %s" % tag_id

    def load(self):
        """
        load all into the DB from google drive.
        :return: None
        """

        scope = ['https://spreadsheets.google.com/feeds']
        path = app.config["GSPREAD_PATH"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
        gc = gspread.authorize(credentials)

        response = urllib2.urlopen(app.config['PROGRAMS_XML'])
        xml = ET.fromstring(response.read())
        program_blocks = xml.findall('.//system-block')

        names = []

        for block in program_blocks:
            name = block.find('name').text
            names.append(name)
            print name
        return "<pre>%s</pre>" % "\n".join(names)

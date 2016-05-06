__author__ = 'ces55739'

import urllib2
from xml.etree import ElementTree as ET
from config import SOAP_URL, CASCADE_LOGIN as AUTH, SITE_ID

from bu_cascade.cascade_connector import Cascade


class BaseViewTools():
    def __init__(self):
        self.cascade_connector = Cascade(SOAP_URL, AUTH, SITE_ID)

    def traverse_xml(self, traverse_xml_callback_function, xml_url, type_to_find, username='get_all'):

        response = urllib2.urlopen(xml_url)
        form_xml = ET.fromstring(response.read())

        matches = []
        for child in form_xml.findall('.//' + type_to_find):
            try:
                try:
                    author = child.find('author').text
                except:
                    author = None

                if (author is not None and username == author) or username == "get_all":
                    matches.append(traverse_xml_callback_function(child))

            except AttributeError:
                continue

        # Todo: maybe add some parameter as a search?
        # sort by created-on date.
        matches = sorted(matches, key=lambda k: k['created-on'])

        return matches

    def read(self, path_or_id, asset_type):
        self.cascade_connector.read(path_or_id, asset_type)

    def publish(self, path_or_id, asset_type):
        self.cascade_connector.publish(path_or_id, asset_type)

    def delete(self, path_or_id, asset_type):
        self.cascade_connector.delete(path_or_id, asset_type)
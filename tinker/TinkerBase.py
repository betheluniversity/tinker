import urllib2
import json
from xml.etree import ElementTree as ET

from bu_cascade.cascade_connector import Cascade
from bu_cascade.assets.block import Block
from bu_cascade.assets.page import Page

from config.config import SOAP_URL, CASCADE_LOGIN as AUTH, SITE_ID


class TinkerBase():
    def __init__(self):
        self.cascade_connector = Cascade(SOAP_URL, AUTH, SITE_ID)

    def traverse_xml(self, traverse_xml_callback_function, xml_url, type_to_find):

        response = urllib2.urlopen(xml_url)
        form_xml = ET.fromstring(response.read())

        matches = []
        for child in form_xml.findall('.//' + type_to_find):
                match = traverse_xml_callback_function(child)
                if match:
                    matches.append(match)

        # Todo: maybe add some parameter as a search?
        # sort by created-on date.
        matches = sorted(matches, key=lambda k: k['created-on'])

        return matches

    def read_block(self, path_or_id):
        b = Block(self.cascade_connector, path_or_id)
        return b

    def read_page(self, path_or_id):
        p = Page(self.cascade_connector, path_or_id)
        p.read_asset()
        return p.structured_data()

    def publish(self, path_or_id, asset_type):
        return self.cascade_connector.publish(path_or_id, asset_type)

    def delete(self, path_or_id, asset_type):
        return self.cascade_connector.delete(path_or_id, asset_type)

    def asset_in_workflow(self, asset_id, asset_type="page"):
        return self.cascade_connector.is_in_workflow(asset_id, asset_type=asset_type)

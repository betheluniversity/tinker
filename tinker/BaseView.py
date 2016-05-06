__author__ = 'ces55739'

import urllib2
from xml.etree import ElementTree as ET
from config import SOAP_URL, CASCADE_LOGIN as AUTH, SITE_ID

from flask import Flask
from flask.ext.classy import FlaskView
from flask import Blueprint
from tinker import app

from bu_cascade.cascade_connector import Cascade
# BaseViewBlueprint = Blueprint('base', __name__, template_folder='templates')


class BaseView(FlaskView):
    def __init__(self):
        self.cascade_connector = Cascade(SOAP_URL, AUTH, SITE_ID)

    def traverse_xml(self, traverse_xml_callback_function, xml_url, username='get_all'):

        response = urllib2.urlopen(xml_url)
        form_xml = ET.fromstring(response.read())

        matches = []
        for child in form_xml.findall('.//system-block'):
            try:
                try:
                    author = child.find('author').text
                except:
                    author = None

                if (author is not None and username == author) or username == "get_all":
                    matches.append(traverse_xml_callback_function(username))

            except AttributeError:
                continue

        # Todo: maybe add some parameter as a search?
        # sort by created-on date.
        matches = sorted(matches, key=lambda k: k['created-on'])

        return matches


# BaseView.register(BaseViewBlueprint)
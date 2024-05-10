# Global
import json
from datetime import datetime

# Packages
from flask import abort, render_template, request
from flask_classy import FlaskView, route
from xml.etree import ElementTree as ET

# Local
from tinker import app, cache
from tinker.admin.sync.sync_metadata import data_to_add
from tinker.admin.sync.sync_controller import SyncController
from tinker.tinker_controller import admin_permissions, requires_auth
from bu_cascade.asset_tools import update, find


class SyncView(FlaskView):
    route_base = '/admin/sync'

    def __init__(self):
        self.base = SyncController()

    def before_request(self, name, **kwargs):
        admin_permissions(self)

    def index(self):
        # get the most recent code
        self.base.git_pull()

        metadata_sets_mapping = self.base.get_metadata_sets_mapping()
        data_definition_mapping = self.base.get_data_definitions_mapping()
        mapping_key_values = self.base.get_mapping_keys()

        return render_template('admin/sync/home.html', **locals())

    @route("/all", methods=['post'])
    def all(self):
        # get the most recent code\
        self.base.git_pull()

        data = data_to_add
        returned_keys = []

        # Get id's and names of md sets and data definitions
        metadata_sets_mapping = self.base.get_metadata_sets_mapping()
        data_definition_mapping = self.base.get_data_definitions_mapping()

        # sync
        returned_keys.extend(self.base.sync_metadata_sets(metadata_sets_mapping))
        returned_keys.extend(self.base.sync_data_definitions(data_definition_mapping))

        return render_template('admin/sync/data.html', **locals())

    @route("/metadata", methods=['post'])
    def metadata(self):
        data = json.loads(request.data)
        id = data['id']
        if not isinstance(id, str):
            return abort(400)
        data = data_to_add

        # Get id's and names of md sets and data definitions
        metadata_sets_mapping = self.base.get_metadata_sets_mapping()
        data_definition_mapping = self.base.get_data_definitions_mapping()

        # sync
        returned_keys = self.base.sync_metadata_set(id)

        return render_template('admin/sync/data.html', **locals())

    @route("/datadefinition", methods=['post'])
    def datadefinition(self):
        data = json.loads(request.data)
        id = data['id']
        if not isinstance(id, str):
            return abort(400)
        data = data_to_add

        # Get id's and names of md sets and data definitions
        metadata_sets_mapping = self.base.get_metadata_sets_mapping()
        data_definition_mapping = self.base.get_data_definitions_mapping()

        # sync
        returned_keys = self.base.sync_data_definition(id)

        return render_template('admin/sync/data.html', **locals())

    # @route("/fix-faculty-bios", methods=['post'])
    # def fix_faculty_bios(self):
    #     from operator import itemgetter
    #     start = False
    #
    #     forms = self.base.traverse_xml(app.config['FACULTY_BIOS_XML_URL'], 'system-page')
    #     forms = sorted(forms, key=itemgetter('last-name'), reverse=False)
    #     for bio in forms:
    #         # if bio['id'] in app.config['FACULTY_BIOS_IDS']:
    #         # if bio['id'] == '58d864ae8c5865fc0d6cc722fc5837c4':
    #         if bio['deactivated'] == 'No':
    #             print(bio['title'])
    #             page = self.base.read_page(bio['id'])
    #             faculty_bio_data, mdata, sdata = page.read_asset()
    #             for node in faculty_bio_data['page']['structuredData']['structuredDataNodes']['structuredDataNode']:
    #                 if node['identifier'] == 'job-titles' and 'text' in node['structuredDataNodes']['structuredDataNode'][11]:
    #                     if 'text' not in node['structuredDataNodes']['structuredDataNode'][7] or node['structuredDataNodes']['structuredDataNode'][7]['text'] == 'No':
    #                         print("changing adjunct...")
    #                         if 'Adjunct' in node['structuredDataNodes']['structuredDataNode'][11]['text']:
    #                             print("Adjunct: Yes")
    #                             node['structuredDataNodes']['structuredDataNode'][7]['text'] = 'Yes'
    #                             node['structuredDataNodes']['structuredDataNode'][11]['text'] = node['structuredDataNodes']\
    #                                 ['structuredDataNode'][11]['text'].replace("Adjunct ", "")
    #                         else:
    #                             print("Adjunct: No")
    #                             node['structuredDataNodes']['structuredDataNode'][7]['text'] = 'No'
    #                     if 'text' not in node['structuredDataNodes']['structuredDataNode'][9] or node['structuredDataNodes']['structuredDataNode'][9]['text'] == 'Neither':
    #                         print("changing emeritus...")
    #                         if ' Emeritus' in node['structuredDataNodes']['structuredDataNode'][11]['text']:
    #                             print("Emeritus")
    #                             node['structuredDataNodes']['structuredDataNode'][9]['text'] = 'Emeritus'
    #                             node['structuredDataNodes']['structuredDataNode'][11]['text'] = node['structuredDataNodes']\
    #                                 ['structuredDataNode'][11]['text'].replace(" Emeritus", "")
    #                         elif 'Emerita' in node['structuredDataNodes']['structuredDataNode'][11]['text']:
    #                             print("Emerita")
    #                             node['structuredDataNodes']['structuredDataNode'][9]['text'] = 'Emerita'
    #                             node['structuredDataNodes']['structuredDataNode'][11]['text'] = node['structuredDataNodes']\
    #                                 ['structuredDataNode'][11]['text'].replace(" Emerita", "")
    #                         else:
    #                             print("Emeritus: Neither")
    #                             node['structuredDataNodes']['structuredDataNode'][9]['text'] = 'Neither'
    #                     node['structuredDataNodes']['structuredDataNode'][8]['text'] = 'Yes'
    #                 if node['identifier'] == 'add-to-bio':
    #                     for option in node['structuredDataNodes']['structuredDataNode']:
    #                         if option['identifier'] != 'options' and 'text' in option:
    #                             option['text'] = option['text'].replace('&', '&amp;')
    #             print("saving...")
    #             page.edit_asset(faculty_bio_data)
    #             print("publishing...\n")
    #             self.base.publish(bio['id'])
    #
    #     status = "Done"
    #     return render_template('faculty-bios/confirm.html', **locals())

    @requires_auth
    @route("/public/sync-prayer-and-memorial", methods=['get'])
    def sync_prayer_and_memorial(self):
        # read in xml
        resp = self.base.tinker_requests(app.config['PRAYER_AND_MEMORIAL_XML'])
        xml = ET.fromstring(resp.content)

        for block in xml.findall('.//system-block'):
            activated = block.find('.//activated')
            date = block.find('.//publication-date')

            try:
                block_date = datetime.fromtimestamp(int(date.text.strip()) / 1000)
                # for each that is activated and more than 10 days old, deactivate it
                if activated.text.lower() == 'activated' and (datetime.now() - block_date).days > 7:
                    block_asset = self.base.read_block(block.attrib.get('id'))
                    update(block_asset.asset, 'activated', 'Deactivated')
                    block_asset.edit_asset(block_asset.asset)
            except:
                pass

        # publish xml
        self.base.publish(app.config['PRAYER_AND_MEMORIAL_ID'])

        return 'success'

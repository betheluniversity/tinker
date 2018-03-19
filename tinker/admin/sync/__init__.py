# Global
import json
import requests
from datetime import datetime

# Packages
from flask import abort, render_template, request
from flask_classy import FlaskView, route
from xml.etree import ElementTree as ET

# Local

from tinker import app, cache
from tinker.admin.sync.sync_metadata import data_to_add
from sync_controller import SyncController
from tinker.admin.publish import PublishManagerController
from tinker.tinker_controller import admin_permissions, requires_auth
from bu_cascade.asset_tools import update


class SyncView(FlaskView):
    route_base = '/admin/sync'

    def __init__(self):
        self.base = SyncController()
        self.publish_controller = PublishManagerController()

    def before_request(self, name, **kwargs):
        admin_permissions(self)

    @cache.memoize(timeout=600)
    def index(self):
        # get the most recent code
        # todo: this will need to be added back in. but it currently breaks on xp (since its using a different branch)
        self.base.git_pull()

        metadata_sets_mapping = self.base.get_metadata_sets_mapping()
        data_definition_mapping = self.base.get_data_definitions_mapping()
        mapping_key_values = self.base.get_mapping_keys()

        return render_template('admin/sync/home.html', **locals())

    @route("/all", methods=['post'])
    def all(self):
        # get the most recent code
        # this currently breaks on xp (since its using a different branch)
        # todo: check if on prod?
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
        data = self.base.dictionary_encoder.encode(json.loads(request.data))
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
        data = self.base.dictionary_encoder.encode(json.loads(request.data))
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

    @requires_auth
    @route("/public/sync-prayer-and-memorial", methods=['get'])
    def sync_prayer_and_memorial(self):
        # read in xml
        resp = requests.get(app.config['PRAYER_AND_MEMORIAL_XML'])
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

    @route("/find-and-replace", methods=['post'])
    def find_and_replace(self):
        data_dict = json.loads(request.data)
        change_metadata_mapping = data_dict.get('change_metadata_mapping')
        change_metadata_old_value = data_dict.get('change_metadata_old_value')
        change_metadata_new_value = data_dict.get('change_metadata_new_value')

        # get mapping
        mapping_keys = self.base.get_mapping_keys()
        # todo: let mapping have a default value, add the logic here
        mapping = mapping_keys.get(change_metadata_mapping)

        # todo: use the search to get the things.
        assets_to_update = self.publish_controller.search(metadata_search=change_metadata_old_value, pages_search=True, blocks_search=True)

        if hasattr(assets_to_update, 'matches') and hasattr(assets_to_update.matches, 'match'):
            for asset in assets_to_update.matches.match:
                try:
                    # todo: check if it has the value
                    # todo: do a cascade read/edit on each page
                    # todo: set this up with a generator with content output below the "Find replace" button
                    pass
                except:
                    continue
        else:
            return 'FAIL'

        return 'DONE'

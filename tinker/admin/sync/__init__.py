# Global
import json
import requests
from datetime import datetime

# Packages
from flask import abort, render_template, request, Response
from flask_classy import FlaskView, route
from xml.etree import ElementTree as ET

# Local
from tinker import app, cache
from tinker.admin.sync.sync_metadata import data_to_add
from sync_controller import SyncController
from tinker.admin.publish import PublishManagerController
from tinker.tinker_controller import admin_permissions, requires_auth
from bu_cascade.asset_tools import find, update


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

    @requires_auth
    @route("/find-and-replace/<change_metadata_mapping>/<change_metadata_old_value>/<change_metadata_new_value>")
    def find_and_replace(self, change_metadata_mapping, change_metadata_old_value, change_metadata_new_value):
        if not change_metadata_mapping or not change_metadata_old_value or not change_metadata_new_value:
            abort(500)

        def generate():
            yield 'Mapping: %s\n' % change_metadata_mapping
            yield 'Old Value: %s\n' % change_metadata_old_value
            yield 'New Value: %s\n' % change_metadata_new_value
            yield '----------------\n'
            # get mapping
            mapping_keys = self.base.get_all_mappings()
            # todo: let mapping have a default value, add the logic here
            mapping = mapping_keys.get(change_metadata_mapping)

            assets_to_update = self.publish_controller.search(metadata_search=change_metadata_old_value, pages_search=True, blocks_search=True)

            # check to make sure there are valid matches
            if hasattr(assets_to_update, 'matches') and hasattr(assets_to_update.matches, 'match'):
                num_assets = len(assets_to_update.matches.match)
                asset_number = 0
                for asset in assets_to_update.matches.match:
                    asset_number += 1
                    asset_path = '(blank)'
                    try:
                        if asset.type == 'page':
                            asset_object = self.base.read_page(asset.id)
                        elif asset.type == 'block':
                            asset_object = self.base.read_block(asset.id)
                        else:
                            continue

                        asset_to_update = asset_object.asset
                        asset_path = '/' + find(asset_to_update, 'path', False)
                        asset_changed = False

                        for mapping_key in mapping:
                            old_values = find(asset_to_update, mapping_key, False)
                            new_values = []
                            if old_values:
                                for value in old_values:
                                    if value == change_metadata_old_value:
                                        new_values.append(change_metadata_new_value)
                                    else:
                                        new_values.append(value)

                            if old_values != new_values:
                                update(asset_to_update, mapping_key, new_values)
                                asset_changed = True

                        if asset_changed:
                            # asset_object.edit_asset(asset_to_update)
                            yield '(%s/%s) success: %s\n' % (asset_number, num_assets, asset_path)
                        else:
                            yield '(%s/%s) skip, nothing to change: %s\n' % (asset_number, num_assets, asset_path)
                    except:
                        yield '(%s/%s) failed: Could not load %s' % (asset_number, num_assets, asset_path)
                        continue
                yield 'finish'
            else:
                yield 'fail: unable to search for matches\n'

        return Response(generate(), mimetype='text/json')

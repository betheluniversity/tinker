# python
import sys

# Packages
from bu_cascade import asset_tools

# Local
from tinker import app
from tinker.tinker_controller import TinkerController
from tinker.admin.sync.sync_metadata import data_to_add


class SyncController(TinkerController):

    def __init__(self):
        super(SyncController, self).__init__()

    # ===================== Metadata Set functions ===================== #
    def sync_metadata_sets(self, metadata_sets):
        returned_keys = []
        for metadata_set_id in metadata_sets:
            returned_keys.extend(self.sync_metadata_set(metadata_set_id))
        return returned_keys

    # sync an individual metadata set
    def sync_metadata_set(self, metadata_set_id):
        metadata_asset = ''
        returned_keys = []
        try:
            asset = self.read_metadata_set(metadata_set_id)
            metadata_asset, empty_variable, empty_variable = asset.get_asset()

            # Attempt to update each applicable key/value for a metadata set.
            # If it doesn't find the field, it returns None
            returned_keys.append(asset_tools.update_metadata_set(metadata_asset, 'roles', data_to_add['roles']))
            returned_keys.append(asset_tools.update_metadata_set(metadata_asset, 'school', data_to_add['school']))
            returned_keys.append(asset_tools.update_metadata_set(metadata_asset, 'department', data_to_add['department'], 'None'))
            returned_keys.append(asset_tools.update_metadata_set(metadata_asset, 'cas-departments', data_to_add['department'], 'None'))
            returned_keys.append(asset_tools.update_metadata_set(metadata_asset, 'adult-undergrad-program', data_to_add['adult-undergrad-program'], 'None'))
            returned_keys.append(asset_tools.update_metadata_set(metadata_asset, 'graduate-program', data_to_add['graduate-program'], 'None'))
            returned_keys.append(asset_tools.update_metadata_set(metadata_asset, 'seminary-program', data_to_add['seminary-program'], 'None'))
            returned_keys.append(asset_tools.update_metadata_set(metadata_asset, 'degree', data_to_add['degree'], 'Select'))

            asset.edit_asset(metadata_asset)
        except:
            self.log_sentry('Sync Metadata Set Error', {
                'metadata_set_id': metadata_set_id,
                'current_asset': metadata_asset
            })
        # TODO: maybe add cascade logger here? would like it in asset.edit_asset, but that's in bu_cascade
        return returned_keys

    def get_metadata_sets_mapping(self):
        metadata_sets_mapping = {}
        metadata_sets = [
            app.config['METADATA_EVENT_ID'],
            app.config['METADATA_ROBUST_ID'],
            app.config['METADATA_JOB_POSTING_ID']
        ]
        for metadata_set_id in metadata_sets:
            asset = self.read_metadata_set(metadata_set_id)
            metadata_asset, empty_variable, empty_variable = asset.get_asset()
            metadata_sets_mapping[metadata_set_id] = metadata_asset['metadataSet']['name']

        return metadata_sets_mapping

    # ===================== Data Definition functions ===================== #
    def sync_data_definitions(self, data_definitions):
        returned_keys = []
        for data_definition_id in data_definitions:
            returned_keys.extend(self.sync_data_definition(data_definition_id))
        return returned_keys

    def sync_data_definition(self, data_definition_id):
        data_definition_asset = ''
        returned_keys = []
        try:
            asset = self.read_datadefinition(data_definition_id)
            data_definition_asset, empty_variable, empty_variable = asset.get_asset()

            # Faculty bios need '&' replaced by 'and'
            faculty_bio_schools = []
            if data_definition_id == app.config['DATA_DEF_FACULTY_BIO_ID']:
                for school in data_to_add['school']:
                    faculty_bio_schools.append(school.replace('&', 'and'))
            else:
                faculty_bio_schools = data_to_add['school']

            # Attempt to update each applicable key/value for a data definition.
            # If it doesn't find the field, it returns None
            returned_keys.append(asset_tools.update_data_definition(data_definition_asset, 'school', faculty_bio_schools))
            returned_keys.append(asset_tools.update_data_definition(data_definition_asset, 'department', data_to_add['department']))
            returned_keys.append(asset_tools.update_data_definition(data_definition_asset, 'adult-undergrad-program', data_to_add['adult-undergrad-program']))
            returned_keys.append(asset_tools.update_data_definition(data_definition_asset, 'graduate-program', data_to_add['graduate-program']))
            returned_keys.append(asset_tools.update_data_definition(data_definition_asset, 'seminary-program', data_to_add['seminary-program']))
            returned_keys.append(asset_tools.update_data_definition(data_definition_asset, 'location', data_to_add['location']))
            returned_keys.append(asset_tools.update_data_definition(data_definition_asset, 'delivery_label', data_to_add['delivery_label']))
            returned_keys.append(asset_tools.update_data_definition(data_definition_asset, 'delivery_subheading', data_to_add['delivery_subheading']))
            returned_keys.append(asset_tools.update_data_definition(data_definition_asset, 'roles', data_to_add['roles']))

            asset.edit_asset(data_definition_asset)
        except:
            self.log_sentry('Sync Data Definition Error', {
                'data_definition_id': data_definition_asset,
                'current_asset': data_definition_asset
            })
        # TODO: maybe add cascade logger here? would like it in asset.edit_asset, but that's in bu_cascade
        return returned_keys

    def get_data_definitions_mapping(self):
        data_definition_mapping = {}
        data_definitions = [
            app.config['DATA_DEF_FACULTY_BIO_ID'],
            app.config['DATA_DEF_PROGRAM_FEED_ID'],
            app.config['DATA_DEF_PROGRAM_BLOCK_ID'],
            app.config['DATA_DEF_PORTAL_CHANNEL_ID'],
            app.config['DATA_DEF_PORTAL_TAB_ID'],
        ]
        for data_definition_id in data_definitions:
            asset = self.read_datadefinition(data_definition_id)
            data_definition_asset, empty_variable, empty_variable = asset.get_asset()
            data_definition_mapping[data_definition_id] = data_definition_asset['dataDefinition']['name']

        return data_definition_mapping

    def git_pull(self):
        # don't pull locally. It's just a bad idea.
        if 'User' not in app.config['INSTALL_LOCATION']:
            import commands
            commands.getoutput(
                "cd %s; git fetch --all; git reset --hard origin/add-reload-to-admin-sync" % app.config['INSTALL_LOCATION'])
            reload(sys.modules['tinker.admin.sync.sync_metadata'])

    def get_mapping_keys(self):
        mapping_key_values = {
            #  this is disabled due to rarely needing it, and also because we have assets with different uses
            # 'school': 'School',
            'department': 'CAS Program',
            'adult-undergrad-program': 'CAPS Program',
            'graduate-program': 'Graduate Program',
            'seminary-program': 'Seminary Program',
            'degree': 'Degree',
            'location': 'Location',
            'delivery_label': 'Delivery Label',
            'delivery_subheading': 'Delivery Subheading'
        }
        return mapping_key_values

    def get_all_mappings(self):
        mapping = {
            # this is disabled due to rarely needing it, and also because we have assets with different uses
            # 'school': ['school'],
            'department': ['department', 'cas-departments'],
            'adult-undergrad-program': ['adult-undergrad-program'],
            'graduate-program': ['graduate-program'],
            'seminary-program': ['seminary-program'],
            'degree': ['degree'],
            'location': ['location'],
            'delivery_label': ['delivery_label'],
            'delivery_subheading': ['delivery_subheading']
        }
        return mapping

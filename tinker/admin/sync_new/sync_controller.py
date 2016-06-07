from tinker.tinker_controller import TinkerController
from bu_cascade import asset_tools


class SyncController(TinkerController):

    def __init__(self):
        super(SyncController, self).__init__()

    def sync_metadata_sets(self, metadata_sets, data_to_add):
        for metadata_set in metadata_sets:
            try:
                asset = self.read_metadata_set(metadata_set)
                metadata_asset, empty_variable, empty_variable = asset.get_asset()

                asset_tools.update_metadata_set(metadata_asset, 'roles', data_to_add['roles'])
                asset_tools.update_metadata_set(metadata_asset, 'school', data_to_add['school'])
                asset_tools.update_metadata_set(metadata_asset, 'department', data_to_add['department'])
                asset_tools.update_metadata_set(metadata_asset, 'cas-departments', data_to_add['department'])
                asset_tools.update_metadata_set(metadata_asset, 'adult-undergrad-program', data_to_add['adult-undergrad-program'])
                asset_tools.update_metadata_set(metadata_asset, 'graduate-program', data_to_add['graduate-program'])
                asset_tools.update_metadata_set(metadata_asset, 'seminary-program', data_to_add['seminary-program'])
                asset_tools.update_metadata_set(metadata_asset, 'degree', data_to_add['degree'])

                asset.edit_asset(metadata_asset)

            except:
                # todo: log an error here
                pass

    # Todo create this
    def sync_data_definitions(self, data_definitions, data_to_add):
        for data_definition in data_definitions:
            try:
                asset = self.read_datadefinition(data_definition)
                data_definition_asset, empty_variable, empty_variable = asset.get_asset()

                # asset_tools.update_data_definition(data_definition_asset, 'roles', data_to_add['roles'])

                # todo: make sure to test with duplicates, not the real data definitions
                # maybe add an additional optional parameter to the update.
                # if "job-titles" in el.attrib[
                # elif "program_filters" in el.attrib['identifier']:  # for Program Feeds | location
                # elif "concentration" in el.attrib['identifier']:  # for Program Blocks | location, cohort delivery
                # elif 'roles' in el.attrib['identifier']:  # for Portal - Tab | roles
                # elif 'sections' in el.attrib['identifier']:  # for Portal - Channel Block | roles
                # elif 'program-search-sync-data' in el.attrib['identifier']:  # for Program Search | school, cohort delivery, degree type


                asset.edit_asset(data_definition_asset)

            except:
                # todo: log an error here
                pass

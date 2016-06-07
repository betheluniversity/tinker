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
                print metadata_asset
                # asset_tools.update(metadata_asset, 'seminary-program', data_to_add['seminary-program'])

            except:
                # todo: log an error here
                pass

    # Todo create this
    def sync_data_definitions(self, data_definitions, data_to_add):
        for data_definition in data_definitions:
            data_definition_asset = self.read_datadefinition(data_definition)
            print data_definition_asset.get_asset()

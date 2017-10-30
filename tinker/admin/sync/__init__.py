# Global
import json

# Packages
from flask import abort, Blueprint, render_template, request
from flask_classy import FlaskView, route

# Local
from tinker.admin.sync.sync_metadata import data_to_add
from sync_controller import SyncController
from tinker.tinker_controller import admin_permissions


SyncBlueprint = Blueprint('sync', __name__, template_folder='templates')


class SyncView(FlaskView):
    route_base = '/admin/sync'

    def __init__(self):
        self.base = SyncController()

    def before_request(self, name, **kwargs):
        admin_permissions(self)

    def index(self):
        # get the most recent code
        # todo: this will need to be added back in. but it currently breaks on xp (since its using a different branch)
        self.base.git_pull()

        metadata_sets_mapping = self.base.get_metadata_sets_mapping()
        data_definition_mapping = self.base.get_data_definitions_mapping()

        return render_template('admin/sync/home.html', **locals())

    @route("/all", methods=['post'])
    def all(self):
        # get the most recent code
        # todo: this will need to be added back in. but it currently breaks on xp (since its using a different branch)
        # self.base.git_pull()

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
        if not (isinstance(id, str) or isinstance(id, unicode)):
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
        if not (isinstance(id, str) or isinstance(id, unicode)):
            return abort(400)
        data = data_to_add

        # Get id's and names of md sets and data definitions
        metadata_sets_mapping = self.base.get_metadata_sets_mapping()
        data_definition_mapping = self.base.get_data_definitions_mapping()

        # sync
        returned_keys = self.base.sync_data_definition(id)

        return render_template('admin/sync/data.html', **locals())

SyncView.register(SyncBlueprint)

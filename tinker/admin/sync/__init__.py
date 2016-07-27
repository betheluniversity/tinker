from flask import Blueprint, render_template, session, abort, request
from flask.ext.classy import FlaskView, route
from flask.ext.wtf import Form

from tinker.admin.sync.sync_metadata import data_to_add
from sync_controller import *

SyncBlueprint = Blueprint('sync', __name__, template_folder='templates')


class SyncView(FlaskView):
    route_base = '/admin/sync'

    def __init__(self):
        self.base = SyncController()

    def before_request(self, name, **kwargs):
        if 'groups' not in session:
            # This if statement block has been added for unit testing purposes
            from tinker.tinker_controller import TinkerController
            tc = TinkerController()
            tc.before_request()
        if 'Administrators' not in session['groups']:
            abort(403)

    def index(self):
        # get the most recent code
        self.base.git_pull()

        metadata_sets_mapping = self.base.get_metadata_sets_mapping()
        data_definition_mapping = self.base.get_data_definitions_mapping()
        form = Form()

        return render_template('sync-home.html', **locals())

    @route("/all", methods=['post'])
    def all(self):
        # get the most recent code
        self.base.git_pull()

        data = data_to_add
        returned_keys = []

        # Get id's and names of md sets and data definitions
        metadata_sets_mapping = self.base.get_metadata_sets_mapping()
        data_definition_mapping = self.base.get_data_definitions_mapping()

        # sync
        returned_keys.extend(self.base.sync_metadata_sets(metadata_sets_mapping))
        returned_keys.extend(self.base.sync_data_definitions(data_definition_mapping))

        return render_template('sync-data.html', **locals())

    @route("/metadata", methods=['post'])
    def metadata(self):
        id = request.form['id']
        data = data_to_add

        # Get id's and names of md sets and data definitions
        metadata_sets_mapping = self.base.get_metadata_sets_mapping()
        data_definition_mapping = self.base.get_data_definitions_mapping()

        # sync
        returned_keys = self.base.sync_metadata_set(id)

        return render_template('sync-data.html', **locals())

    @route("/datadefinition", methods=['post'])
    def datadefinition(self):
        id = request.form['id']
        data = data_to_add

        # Get id's and names of md sets and data definitions
        metadata_sets_mapping = self.base.get_metadata_sets_mapping()
        data_definition_mapping = self.base.get_data_definitions_mapping()

        # sync
        returned_keys = self.base.sync_data_definition(id)

        return render_template('sync-data.html', **locals())

SyncView.register(SyncBlueprint)

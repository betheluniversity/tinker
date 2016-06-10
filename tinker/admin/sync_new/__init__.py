from flask import Blueprint, render_template, session, abort, request
from flask.ext.classy import FlaskView, route

from tinker.admin.sync_new.metadata import data_to_add
from sync_controller import *

SyncBlueprint = Blueprint('sync', __name__, template_folder='templates')


class SyncView(FlaskView):
    route_base = '/admin/sync'

    def __init__(self):
        self.base = SyncController()

    def before_request(self, name, **kwargs):
        if 'Administrators' not in session['groups']:
            abort(403)

    def index(self):
        metadata_sets_mapping = self.base.get_metadata_sets_mapping()
        data_definition_mapping = self.base.get_data_definitions_mapping()

        return render_template('sync-home.html', **locals())

    def all(self):
        data = data_to_add
        returned_keys = []
        # Todo: clean this up
        # Todo: This pull works the second time. maybe call the pull from a url?
        # don't pull locally. It's just a bad idea.
        if 'User' not in app.config['INSTALL_LOCATION']:
            import commands
            commands.getoutput(
                "cd " + app.config['INSTALL_LOCATION'] + "; git fetch --all; git reset --hard origin/master")

        metadata_sets_mapping = self.base.get_metadata_sets_mapping()
        returned_keys.extend(self.base.sync_metadata_sets(metadata_sets_mapping))

        data_definition_mapping = self.base.get_data_definitions_mapping()
        returned_keys.extend(self.base.sync_data_definitions(data_definition_mapping))

        return render_template('sync-home.html', **locals())

    @route("/metadata", methods=['post'])
    def metadata(self):
        id = request.form['id']
        data = data_to_add
        returned_keys = self.base.sync_metadata_set(id)

        metadata_sets_mapping = self.base.get_metadata_sets_mapping()
        data_definition_mapping = self.base.get_data_definitions_mapping()

        return render_template('sync-data.html', **locals())

    @route("/datadefinition", methods=['post'])
    def datadefinition(self):
        id = request.form['id']

        data = data_to_add
        returned_keys = self.base.sync_data_definition(id)

        metadata_sets_mapping = self.base.get_metadata_sets_mapping()
        data_definition_mapping = self.base.get_data_definitions_mapping()

        return render_template('sync-data.html', **locals())

SyncView.register(SyncBlueprint)

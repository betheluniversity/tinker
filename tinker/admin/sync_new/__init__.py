from flask import Blueprint, render_template, abort, request
from flask.ext.classy import FlaskView, route

from tinker.admin.sync_new.metadata import data_to_add
from sync_controller import *

SyncBlueprint = Blueprint('sync', __name__, template_folder='templates')


# Todo: update the templates
class SyncView(FlaskView):
    route_base = '/admin/sync'

    def __init__(self):
        self.base = SyncController()

    def before_request(self, name, **kwargs):
        # if 'Administrators' in session['groups']
        pass

    def index(self):
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

        metadata_sets = [
            app.config['METADATA_EVENT_ID'],
            app.config['METADATA_ROBUST_ID'],
            app.config['METADATA_JOB_POSTING_ID'],
            app.config['METADATA_PORTAL_ROLES_ID']
        ]
        returned_keys.extend(self.base.sync_metadata_sets(metadata_sets))

        data_definitions = [
            app.config['DATA_DEF_FACULTY_BIO_ID'],
            app.config['DATA_DEF_PROGRAM_FEED_ID'],
            app.config['DATA_DEF_PROGRAM_BLOCK_ID'],
            app.config['DATA_DEF_PORTAL_CHANNEL_ID'],
            app.config['DATA_DEF_PORTAL_TAB_ID'],
            app.config['DATA_DEF_PROGRAM_SEARCH_ID']
        ]
        returned_keys.extend(self.base.sync_data_definitions(data_definitions))

        return render_template('sync.html', **locals())

    # sync a single metadata set
    def metadata(self, id):
        data = data_to_add
        returned_keys = self.base.sync_metadata_set(id)
        return render_template('sync.html', **locals())

    # sync a single data definition
    def datadefinition(self, id):
        data = data_to_add
        returned_keys = self.base.sync_data_definition(id)
        return render_template('sync.html', **locals())

SyncView.register(SyncBlueprint)

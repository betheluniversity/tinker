from flask import Blueprint, render_template, abort, request
from flask.ext.classy import FlaskView, route

from tinker import app
from sync_controller import *
from metadata import data_to_add

SyncBlueprint = Blueprint('sync', __name__, template_folder='templates')


class SyncView(FlaskView):
    route_base = '/admin/sync'

    def __init__(self):
        self.base = SyncController()

    def before_request(self, name, **kwargs):
        # todo do this
        print 'sync before request'

    def index(self):
        return render_template('sync-home.html', **locals())

    def all(self):
        # Todo: clean this up
        # don't pull locally. It's just a bad idea.
        if 'User' not in app.config['INSTALL_LOCATION']:
            import commands
            commands.getoutput(
                "cd " + app.config['INSTALL_LOCATION'] + "; git fetch --all; git reset --hard origin/master")

        metadata_sets = [
            # app.config['METADATA_EVENT_ID'],
            'f28775138c5865134b131aec94dc5286'
            # app.config['METADATA_ROBUST_ID'],
            # app.config['METADATA_JOB_POSTING_ID'],
            # app.config['METADATA_PORTAL_ROLES_ID']
        ]
        self.base.sync_metadata_sets(metadata_sets, data_to_add)

        # data_definitions = [
        #     app.config['DATA_DEF_FACULTY_BIO_ID'],
        #     app.config['DATA_DEF_PROGRAM_FEED_ID'],
        #     app.config['DATA_DEF_PROGRAM_BLOCK_ID'],
        #     app.config['DATA_DEF_PORTAL_CHANNEL_ID'],
        #     app.config['DATA_DEF_PORTAL_CHANNEL_ID'],
        #     app.config['DATA_DEF_PORTAL_TAB_ID'],
        #     app.config['DATA_DEF_PROGRAM_SEARCH_ID']
        # ]
        # self.base.sync_data_definitions(data_definitions, data_to_add)

        return render_template('sync.html', **locals())


SyncView.register(SyncBlueprint)

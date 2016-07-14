import logging

# flask
from flask import Flask, Blueprint
from flask.ext.classy import FlaskView
from flask import render_template, send_file

# flask extensions
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cors import CORS

app = Flask(__name__)
app.config.from_object('config.config')
db = SQLAlchemy(app)
cors = CORS(app)

from raven.contrib.flask import Sentry
sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO)



cache = Cache(app, config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

# create logging
if not app.debug:
    import logging
    from logging import FileHandler
    file_handler = FileHandler(app.config['INSTALL_LOCATION'] + '/error.log')
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)




# Import routes
from tinker.events.views import event_blueprint
from tinker.faculty_bio.views import faculty_bio_blueprint

app.register_blueprint(event_blueprint, url_prefix='/event')
app.register_blueprint(faculty_bio_blueprint, url_prefix='/faculty-bio')

# New importing of routes and blueprints
from tinker.e_announcements import EAnnouncementsBlueprint
from tinker.admin.cache import CacheBlueprint
from tinker.office_hours import OfficeHoursBlueprint
from tinker.admin.blink_roles import BlinkRolesBlueprint
from tinker.admin.sync import SyncBlueprint
from tinker.admin.publish import PublishManagerBlueprint
from tinker.admin.redirects import RedirectsBlueprint
from tinker.views import BaseBlueprint

app.register_blueprint(EAnnouncementsBlueprint)
app.register_blueprint(CacheBlueprint)
app.register_blueprint(OfficeHoursBlueprint)
app.register_blueprint(BlinkRolesBlueprint)
app.register_blueprint(SyncBlueprint)
app.register_blueprint(PublishManagerBlueprint)
app.register_blueprint(RedirectsBlueprint)
app.register_blueprint(BaseBlueprint)

# Import error handling
import error

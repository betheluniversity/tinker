import logging

# flask
from flask import Flask

# flask extensions
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cors import CORS
from raven.contrib.flask import Sentry
from flask_wtf.csrf import CsrfProtect

app = Flask(__name__)
app.config.from_object('config.config')
db = SQLAlchemy(app)
cors = CORS(app)

sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO)

# todo: is this used?
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

# todo: is this used?
# create logging
if not app.debug:
    import logging
    from logging import FileHandler
    file_handler = FileHandler(app.config['INSTALL_LOCATION'] + '/error.log')
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)

# Import routes -- These will be removed when we are done with the refactor
from tinker.events.views import event_blueprint
app.register_blueprint(event_blueprint, url_prefix='/event')

# New importing of routes and blueprints
from tinker.views import BaseBlueprint
from tinker.admin.cache import CacheBlueprint
from tinker.admin.blink_roles import BlinkRolesBlueprint
from tinker.admin.sync import SyncBlueprint
from tinker.admin.publish import PublishManagerBlueprint
from tinker.admin.redirects import RedirectsBlueprint
from tinker.e_announcements import EAnnouncementsBlueprint
from tinker.faculty_bio import FacultyBioBlueprint
from tinker.office_hours import OfficeHoursBlueprint

app.register_blueprint(BaseBlueprint)
app.register_blueprint(CacheBlueprint)
app.register_blueprint(BlinkRolesBlueprint)
app.register_blueprint(SyncBlueprint)
app.register_blueprint(PublishManagerBlueprint)
app.register_blueprint(RedirectsBlueprint)
app.register_blueprint(EAnnouncementsBlueprint)
app.register_blueprint(FacultyBioBlueprint)
app.register_blueprint(OfficeHoursBlueprint)

CsrfProtect(app)

# todo: is this used?
# Import error handling
import error

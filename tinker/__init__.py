import logging

# flask
from flask import Flask

# flask extensions
from flask.ext.sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry
from flask_wtf.csrf import CsrfProtect
from bu_cascade.cascade_connector import Cascade

app = Flask(__name__)
app.config.from_object('config.config')
db = SQLAlchemy(app)

cascade_connector = Cascade(app.config['SOAP_URL'], app.config['CASCADE_LOGIN'], app.config['SITE_ID'])

<<<<<<< HEAD
<<<<<<< HEAD
# The below is the flask-cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

# The below is for Flask logging
=======
sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO, logging_exclusions=("werkzeug",))
=======
sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO)
>>>>>>> origin/create-base-view

>>>>>>> origin/create-base-view
# create logging
if not app.debug:
    from logging import FileHandler
    file_handler = FileHandler(app.config['INSTALL_LOCATION'] + '/error.log')
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)


# New importing of routes and blueprints
from tinker.views import BaseBlueprint
from tinker.admin.cache import CacheBlueprint
from tinker.admin.blink_roles import BlinkRolesBlueprint
from tinker.admin.program_search import ProgramSearchBlueprint
from tinker.admin.sync import SyncBlueprint
from tinker.admin.publish import PublishManagerBlueprint
from tinker.admin.program_search import ProgramSearchBlueprint
from tinker.admin.redirects import RedirectsBlueprint
from tinker.e_announcements import EAnnouncementsBlueprint
from tinker.faculty_bios import FacultyBioBlueprint
from tinker.office_hours import OfficeHoursBlueprint
from tinker.events import EventsBlueprint

app.register_blueprint(BaseBlueprint)
app.register_blueprint(CacheBlueprint)
app.register_blueprint(BlinkRolesBlueprint)
app.register_blueprint(ProgramSearchBlueprint)
app.register_blueprint(SyncBlueprint)
app.register_blueprint(PublishManagerBlueprint)
app.register_blueprint(ProgramSearchBlueprint)
app.register_blueprint(RedirectsBlueprint)
app.register_blueprint(EAnnouncementsBlueprint)
app.register_blueprint(EventsBlueprint)
app.register_blueprint(FacultyBioBlueprint)
app.register_blueprint(OfficeHoursBlueprint)

CsrfProtect(app)

<<<<<<< HEAD
# Used to import error.py, which handles 403, 404, 500, and 503 server-errors
# Import error handling
import error

=======
# Import global HTTP error code handling
import error
<<<<<<< HEAD
>>>>>>> origin/create-base-view
=======
from tinker_controller import TinkerController


@app.before_request
def before_request():
    base = TinkerController()
    base.before_request()
>>>>>>> origin/create-base-view

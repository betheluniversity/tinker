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

cascade_connector = Cascade(app.config['SOAP_URL'], app.config['CASCADE_LOGIN'], app.config['SITE_ID'], app.config['STAGING_DESTINATION_ID'])

sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO)

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
from tinker.faculty_bios import FacultyBiosBlueprint
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
app.register_blueprint(FacultyBiosBlueprint)
app.register_blueprint(OfficeHoursBlueprint)

CsrfProtect(app)

# Import global HTTP error code handling
import error
from tinker_controller import TinkerController


@app.before_request
def before_request():
    base = TinkerController()
    base.before_request()

#ignore
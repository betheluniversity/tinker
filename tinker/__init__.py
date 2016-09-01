import logging
import platform

# flask
from flask import Flask

# flask extensions
from flask_sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry
from flask_wtf.csrf import CsrfProtect
from bu_cascade.cascade_connector import Cascade

app = Flask(__name__)

if "testing" not in platform.node():
    app.config.from_object('config.config')
else:
    keywords = ['DATA_DEF_PORTAL_TAB_ID','TEST_USER','OFFICE_HOURS_STANDARD_BLOCK','EVENTS_BASE_ASSET',
                'IMAGE_WITH_DEFAULT_IMAGE_BASE_ASSET','PROGRAM_SEARCH_CSV','ENVIRON','API_USERNAME',
                'DATA_DEF_FACULTY_BIO_ID','SOAP_URL','REDIRECTS_FILE_PATH','E_ANNOUNCEMENT_WORKFLOW_ID','E_ANN_XML_URL',
                'INSTALL_LOCATION','TEMPLATE_ID','E_ANNOUNCEMENTS_XML_ID','THUMBOR_RESULT_STORAGE_LOCATION',
                'EVENTS_XML_URL','DATA_DEF_PROGRAM_SEARCH_ID','UPLOAD_FOLDER',
                'WSDL_URL','FACULTY_LISTING_CAS_ID','STAGING_DESTINATION_ID',
                'SQLALCHEMY_MIGRATE_REPO','FACULTY_BIOS_BASE_ASSET','FACULTY_BIOS_XML_ID',
                'METADATA_PORTAL_ROLES_ID','METADATA_EVENT_ID','DATA_DEF_PORTAL_CHANNEL_ID','API_PASSWORD',
                'EVENT_XML_ID','FOUNDATION_USE_CDN','FACULTY_BIOS_WORKFLOW_CAS_ID',
                'CAMPAIGN_MONITOR_KEY','ADMINS','OFFICE_HOURS_XML_URL',
                'PRESERVE_CONTEXT_ON_EXCEPTION','WUFOO_BASE_URL','BASE_ASSET_EVENT_FOLDER','SENTRY_URL',
                'SESSION_COOKIE_PATH','SITE_ID','LOGGER_NAME','CLIENT_ID','CASCADE_LOGIN','SECRET_KEY',
                'THUMBOR_CALL_CMD','DATA_DEF_PROGRAM_FEED_ID','CACHE_DEFAULT_TIMEOUT','GITHUB_CREDENTIALS',
                'DATA_DEF_PROGRAM_BLOCK_ID','API_URL','TESTING','E_ANN_ADMINS',
                'FACULTY_BIOS_ADMINS','METADATA_JOB_POSTING_ID','FACULTY_BIOS_WORKFLOW_SEM_ID',
                'FACULTY_LISTING_CAPS_ID','SQLALCHEMY_DATABASE_URI','BASE_URL',
                'FACULTY_BIOS_XML_URL','METADATA_ROBUST_ID','E_ANN_BASE_ASSET','EVENTS_FOLDER_ID','DEBUG',
                'EVENTS_WORKFLOW_ID','FOUNDATION_USE_MINIFIED','BASE_ASSET_BASIC_FOLDER',
                'FACULTY_LISTING_SEM_ID','FACULTY_BIOS_WORKFLOW_CAPSGS_ID',
                'PROPAGATE_EXCEPTIONS','API_KEYS','FACULTY_LISTING_GS_ID',
                'WSAPI_SECRET','THUMBOR_STORAGE_LOCATION',
                'FACULTY_BIO_XML_ID','PROGRAMS_XML']
    for kw in keywords:
        app.config.from_envvar(kw)

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
from tinker.faculty_bio import FacultyBioBlueprint
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

from tinker.unit_test_interface import UnitTestBlueprint
app.register_blueprint(UnitTestBlueprint)

CsrfProtect(app)

# Import global HTTP error code handling
import error
from tinker_controller import TinkerController


@app.before_request
def before_request():
    base = TinkerController()
    base.before_request()

#ignore
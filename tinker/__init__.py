# The ignore DeprecationWarning code here is because flask is still referencing request.json somewhere in its code,
# when it should instead be getting request.get_json(). Werkzeug allows it, but throws the deprecation warning. As of
# Sept. 22, 2016, that is the only warning being thrown. Periodically this ignore should be commented out to make sure
# our code is not throwing the deprecated warnings
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import logging
import os
import platform

# flask
from flask import Flask, url_for

# flask extensions
from flask_sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry
from flask_wtf.csrf import CsrfProtect
from bu_cascade.cascade_connector import Cascade

app = Flask(__name__)

if "testing" not in platform.node():
    app.config.from_object('config.config')
else:
    import ast, glob
    app.debug = True
    keywords = []

    dist_path = os.path.dirname(__file__) + "/../config/dist"
    os.chdir(dist_path)
    for file in glob.glob("*.dist"):
        with open(dist_path + "/" + file) as f:
            keyword_lines = f.readlines()
            for line in keyword_lines:
                possible_keyword = line.split(" = ")[0]
                if possible_keyword.isupper():
                    keywords.append(possible_keyword)
    for kw in keywords:
        if kw in ['_basedir', 'SQLALCHEMY_DATABASE_URI', 'SQLALCHEMY_MIGRATE_REPO', 'PROGRAM_SEARCH_CSV', 'REDIRECTS_FILE_PATH']:
            continue
        value = os.environ[kw]
        if "[" in value or "{" in value:
            value = ast.literal_eval(os.environ[kw])
        app.config[kw] = value

    # These config vars require code operations, and aren't just values
    _basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['_basedir'] = _basedir
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(_basedir, '../config/app.db.back')
    app.config['SQLALCHEMY_MIGRATE_REPO'] = os.path.join(_basedir, 'db_repository')
    app.config['PROGRAM_SEARCH_CSV'] = os.path.join(_basedir, '../programs.csv')
    app.config['REDIRECTS_FILE_PATH'] = os.path.join(_basedir, '../redirects.txt')

db = SQLAlchemy(app)

cascade_connector = Cascade(app.config['SOAP_URL'], app.config['CASCADE_LOGIN'], app.config['SITE_ID'], app.config['STAGING_DESTINATION_ID'])

try:
    unit_testing = os.environ['unit_testing']
    print "os.environ:unit_testing =", unit_testing
    if unit_testing == "True":
        app.config['SENTRY_URL'] = ''
except:
    pass

sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO)

# create logging
if not app.debug:
    from logging import FileHandler
    file_handler = FileHandler(app.config['INSTALL_LOCATION'] + '/error.log')
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)


# This method is placed here to fix an import dependency problem; must be above the UnitTestBlueprint import
def get_url_from_path(path, **kwargs):
    app.config['SERVER_NAME'] = '127.0.0.1:5000'  # This will need to be changed to tinker(.xp).bethel.edu on production
    with app.app_context():
        url_to_return = url_for(path, **kwargs)
        if app.config['SERVER_NAME'] in url_to_return:
            url_to_return = url_to_return.split(app.config['SERVER_NAME'])[1]
        return url_to_return


# New importing of routes and blueprints
from tinker.views import BaseBlueprint
from tinker.admin.cache import CacheBlueprint
from tinker.admin.blink_roles import BlinkRolesBlueprint
from tinker.admin.program_search import ProgramSearchBlueprint
from tinker.admin.sync import SyncBlueprint
from tinker.admin.publish import PublishBlueprint
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
app.register_blueprint(PublishBlueprint)
app.register_blueprint(ProgramSearchBlueprint)
app.register_blueprint(RedirectsBlueprint)
app.register_blueprint(EAnnouncementsBlueprint)
app.register_blueprint(EventsBlueprint)
app.register_blueprint(FacultyBiosBlueprint)
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
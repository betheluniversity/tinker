import logging
import os
import platform

# flask
from flask import Flask, url_for
from flask import session
from flask import make_response
from flask import redirect
from flask import request
from flask import render_template
from flask import Blueprint

# flask extensions
import flask_profiler
from flask_classy import FlaskView
from flask_sqlalchemy import SQLAlchemy
from flask_cache import Cache
from raven.contrib.flask import Sentry
from bu_cascade.cascade_connector import Cascade

app = Flask(__name__)

if "testing" not in platform.node():
    TRAVIS_TESTING = False
    app.config.from_object('config.config')
else:
    import ast, glob
    TRAVIS_TESTING = True
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
            try:
                value = ast.literal_eval(os.environ[kw])
            except SyntaxError:
                print "Errored on " + kw + ": " + value
        app.config[kw] = value

    # These config vars require code operations, and aren't just values
    _basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['_basedir'] = _basedir
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(_basedir, '../config/app.db.back')
    app.config['SQLALCHEMY_MIGRATE_REPO'] = os.path.join(_basedir, 'db_repository')
    app.config['PROGRAM_SEARCH_CSV'] = os.path.join(_basedir, '../programs.csv')
    app.config['REDIRECTS_FILE_PATH'] = os.path.join(_basedir, '../redirects.txt')

app.config["flask_profiler"] = {
    "enabled": True,
    "storage": {
        "engine": "sqlite",
        "FILE": app.config['INSTALL_LOCATION'] + '/flask_profiler.sql'
    },
    "ignore": [
        "/static/*"
    ]
}

prod = app.config['ENVIRON'] == 'prod'
if prod:
    app.config["flask_profiler"]["basicAuth"] = {
        "enabled": True,
        "username": app.config['CASCADE_LOGIN']['username'],
        "password": app.config['CASCADE_LOGIN']['password']
    }

db = SQLAlchemy(app)

cascade_connector = Cascade(app.config['SOAP_URL'], app.config['CASCADE_LOGIN'], app.config['SITE_ID'], app.config['STAGING_DESTINATION_ID'])

sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO)

# create logging
if not app.debug:
    from logging import FileHandler
    file_handler = FileHandler(app.config['INSTALL_LOCATION'] + '/error.log')
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)


# This method is placed here to fix an import dependency problem; must be above the UnitTestBlueprint import
def get_url_from_path(path, **kwargs):
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
from tinker.news import NewsBlueprint
from tinker.admin.user_roles import UserRolesBlueprint

app.register_blueprint(BaseBlueprint)
app.register_blueprint(CacheBlueprint)
app.register_blueprint(BlinkRolesBlueprint)
app.register_blueprint(ProgramSearchBlueprint)
app.register_blueprint(SyncBlueprint)
app.register_blueprint(PublishBlueprint)
app.register_blueprint(ProgramSearchBlueprint)
app.register_blueprint(RedirectsBlueprint)
app.register_blueprint(EAnnouncementsBlueprint)
app.register_blueprint(FacultyBiosBlueprint)
app.register_blueprint(OfficeHoursBlueprint)
app.register_blueprint(EventsBlueprint)
app.register_blueprint(NewsBlueprint)
app.register_blueprint(UserRolesBlueprint)


from tinker.unit_test_interface import UnitTestBlueprint
app.register_blueprint(UnitTestBlueprint)

# Import global HTTP error code handling
import error
from tinker_controller import TinkerController


@app.before_request
def before_request():
    base = TinkerController()
    base.before_request()


@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    resp = make_response(redirect(app.config['LOGOUT_URL']))
    resp.set_cookie('MOD_AUTH_CAS_S', '', expires=0)
    resp.set_cookie('MOD_AUTH_CAS', '', expires=0)
    return resp

if not TRAVIS_TESTING:
    flask_profiler.init_app(app)

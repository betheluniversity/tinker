# Global
import logging
import os
import platform

# Packages
import flask_profiler
from bu_cascade.cascade_connector import Cascade
from flask import Flask, make_response, redirect, session, url_for
from flask.ext.cache import Cache
from flask_sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry

app = Flask(__name__)

if "travis" not in platform.node():
    TRAVIS_TESTING = False
    app.config.from_object('config.config')
else:
    import ast
    import glob
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
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(_basedir, '../config/app.db')
    app.config['SQLALCHEMY_MIGRATE_REPO'] = os.path.join(_basedir, 'db_repository')
    app.config['PROGRAM_SEARCH_CSV'] = os.path.join(_basedir, '../programs.csv')
    app.config['REDIRECTS_FILE_PATH'] = os.path.join(_basedir, '../redirects.txt')

# create logging
if not app.debug:
    from logging import FileHandler
    file_handler = FileHandler(app.config['INSTALL_LOCATION'] + '/error.log')
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)

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

if app.config['ENVIRON'] != 'prod':
    cache = Cache(app, config={'CACHE_TYPE': 'simple'})
else:
    cache = Cache(app, config={
        'CACHE_TYPE': 'redis',
        # The default value for CACHE_REDIS_HOST is localhost/127.0.0.1, but if we ever wanted to make it accessible by
        # another server, say h20, we could change this value to be the IP of h12 itself
        # 'CACHE_REDIS_HOST': 'localhost',

        # Likewise, the default port number is 6379, but we can set it here if we want to make Redis publicly accessible
        # 'CACHE_REDIS_PORT': 6379,

        # Finally, if we make it accessible, this is how we would set it to be password-protected
        # 'CACHE_REDIS_PASSWORD': None,

        # This key is needed in case we want to call cache.clear(); Redis' backend implementation in Flask-Cache is
        # finicky and should have a prefix so that .clear() knows which values to remove.
        'CACHE_KEY_PREFIX': 'tinker-'
    })

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


a = 0
a = a['BROKEN']

from tinker.unit_test_interface import UnitTestBlueprint
app.register_blueprint(UnitTestBlueprint)

from tinker import error
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

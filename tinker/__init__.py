import logging

# flask
from flask import Flask
from flask import session

# flask extensions
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cors import CORS
from flask_wtf.csrf import CsrfProtect


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
cors = CORS(app)

from raven.contrib.flask import Sentry
sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO, logging_exclusions=("werkzeug",))

from tinker.admin.redirects import models
from tinker.admin.program_search import models
from tinker import tools

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
import views
from tinker.events.views import event_blueprint
from tinker.faculty_bio.views import faculty_bio_blueprint
from tinker.admin.redirects.views import redirect_blueprint
from tinker.heading_upgrade.views import heading_upgrade
from tinker.e_announcements.views import e_announcements_blueprint
from tinker.admin.sync.views import sync_blueprint
from tinker.admin.publish.views import publish_blueprint
from tinker.admin.roles.views import blink_roles_blueprint
from tinker.admin.cache.views import cache_blueprint

app.register_blueprint(event_blueprint, url_prefix='/event')
app.register_blueprint(faculty_bio_blueprint, url_prefix='/faculty-bio')
app.register_blueprint(heading_upgrade, url_prefix='/heading-upgrade')
app.register_blueprint(e_announcements_blueprint, url_prefix='/e-announcement')
app.register_blueprint(sync_blueprint, url_prefix='/admin/sync')
app.register_blueprint(publish_blueprint, url_prefix='/admin/publish-manager')
app.register_blueprint(blink_roles_blueprint, url_prefix='/admin/blink-roles')
app.register_blueprint(cache_blueprint, url_prefix='/admin/cache-clear')
app.register_blueprint(redirect_blueprint, url_prefix='/admin/redirect')

from tinker.admin.program_search import ProgramSearchView
ProgramSearchView.register(app, route_prefix='admin')


CsrfProtect(app).exempt(redirect_blueprint)

# Import error handling
import error

# ensure session before each request
@app.before_request
def before_request():
    try:
        tools.init_user()
        app.logger.debug(session['username'])
    except:
        app.logger.debug("failed to init")


@app.route('/cache-clear/<path:img_path>')
@app.route('/cache-clear')
def cache_test(img_path=None):
    if not img_path:
        img_path = '/academics/faculty/images/lundberg-kelsey.jpg'
    return tools.clear_image_cache(img_path)


@app.route('/sherie')
def peanut():
    from flask import render_template
    return render_template('sherie.html')


@app.route('/read/<read_id>')
def read_route(read_id):
    from web_services import read
    return "<pre>%s</pre>" % str(read(read_id, type='block'))


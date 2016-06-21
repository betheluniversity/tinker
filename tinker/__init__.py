import logging

# flask
from flask import Flask

# flask extensions
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cors import CORS
from flask_wtf.csrf import CsrfProtect
from flask import session


app = Flask(__name__)
app.config.from_object('config.config')
db = SQLAlchemy(app)
cors = CORS(app)

from raven.contrib.flask import Sentry
sentry = Sentry(app, dsn=app.config['SENTRY_URL'], logging=True, level=logging.INFO)

from tinker_controller import TinkerController
base = TinkerController()

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
from tinker.admin.sync.views import sync_blueprint
from tinker.admin.publish.views import publish_blueprint
from tinker.admin.roles.views import blink_roles_blueprint
from tinker.admin.cache.views import cache_blueprint

app.register_blueprint(event_blueprint, url_prefix='/event')
app.register_blueprint(faculty_bio_blueprint, url_prefix='/faculty-bio')
app.register_blueprint(heading_upgrade, url_prefix='/heading-upgrade')
app.register_blueprint(sync_blueprint, url_prefix='/admin/sync')
app.register_blueprint(publish_blueprint, url_prefix='/admin/publish-manager')
app.register_blueprint(blink_roles_blueprint, url_prefix='/admin/blink-roles')
app.register_blueprint(cache_blueprint, url_prefix='/admin/cache-clear')
app.register_blueprint(redirect_blueprint, url_prefix='/admin/redirect')


# New importing of routes and blueprints
from tinker.e_announcements import EAnnouncementsBlueprint
app.register_blueprint(EAnnouncementsBlueprint)

from tinker.office_hours import OfficeHoursBlueprint
app.register_blueprint(OfficeHoursBlueprint)

csrf = CsrfProtect(app)
csrf.exempt(redirect_blueprint)
csrf.exempt(OfficeHoursBlueprint)

# Import error handling
import error

# ensure session before each request
@app.before_request
def before_request():
    base.before_request()


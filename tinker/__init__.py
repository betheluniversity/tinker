# flask
from flask import Flask
from flask import session

# flask extensions
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cors import CORS

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
cors = CORS(app)

from tinker.wufoo import models
from tinker.redirects import models
from tinker import tools

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

# create logging
if not app.debug:
    import logging
    from logging import FileHandler
    file_handler = FileHandler(app.config['INSTALL_LOCATION'] + '/error.log')
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

if not app.debug and app.config['ENVIRON'] is not 'test':
    from logging.handlers import SMTPHandler
    mail_handler = SMTPHandler('127.0.0.1',
                               'tinker@bethel.edu',
                               app.config['ADMINS'], 'That was an unqualified, failure.')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

# Import routes
import views
from tinker.events.views import event_blueprint
from tinker.faculty_bios.views import faculty_bio_blueprint
from tinker.redirects.views import redirect_blueprint
from tinker.heading_upgrade.views import heading_upgrade
app.register_blueprint(event_blueprint, url_prefix='/event')
app.register_blueprint(faculty_bio_blueprint, url_prefix='/faculty-bios')
app.register_blueprint(redirect_blueprint, url_prefix='/redirect')
app.register_blueprint(heading_upgrade, url_prefix='/heading-upgrade')

# Import error handling
import error


# ensure session before each request
@app.before_request
def before_request():
    try:
        tools.init_user()
        app.logger.info(session['username'])
    except:
        app.logger.info("failed to init")


@app.route('/cache-test/<path:img_path>')
@app.route('/cache-test')
def cache_test(img_path=None):
    if not img_path:
        img_path = '/academics/faculty/images/lundberg-kelsey.jpg'
    return tools.clear_image_cache(img_path)

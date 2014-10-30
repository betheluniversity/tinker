#python


#flask
from flask import Flask
from flask import session

from tinker import tools


#flask extensions
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cors import CORS

app = Flask(__name__)
app.config.from_object('config')
#Foundation(app)
db = SQLAlchemy(app)
cors = CORS(app)

from tinker.wufoo import models
from tinker.redirects import models

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

#create logging
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

#Import routes
import views
from tinker.events.views import event_blueprint
from tinker.faculty_bios.views import faculty_bio_blueprint
from tinker.wufoo.views import wufoo_blueprint
from tinker.redirects.views import redirect_blueprint
from tinker.heading_upgrade.views import heading_upgrade
app.register_blueprint(event_blueprint, url_prefix='/event')
app.register_blueprint(faculty_bio_blueprint, url_prefix='/faculty-bios')
app.register_blueprint(wufoo_blueprint, url_prefix='/wufoo')
app.register_blueprint(redirect_blueprint, url_prefix='/redirect')
app.register_blueprint(heading_upgrade, url_prefix='/heading-upgrade')

#Import error handling
import error


#ensure session before each request
@app.before_request
def before_request():
    tools.init_user()


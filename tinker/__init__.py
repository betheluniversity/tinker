#python
import os

#flask
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


#flask extensions
from flask.ext.foundation import Foundation
##from flask.ext.cache import Cache


app = Flask(__name__)
app.config.from_object('config')
##cache = Cache(app, config={'CACHE_TYPE': 'simple'})
##cache.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

#create logging
if not app.debug:
    import logging
    from logging import FileHandler
    file_handler = FileHandler(app.config['INSTALL_LOCATION'] + '/error.log')
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)


#Import routes
import views

#Blueprints
from tinker.redirects.views import redirect_blueprint
app.register_blueprint(redirect_blueprint, url_prefix='/redirect')

#Import error handling
import error
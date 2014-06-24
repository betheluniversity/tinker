#python
import os

#flask
from flask import Flask

#flask extensions
from flask.ext.foundation import Foundation
from flask.ext.cache import Cache


app = Flask(__name__)
Foundation(app)
app.config.from_object('config')
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

cache.init_app(app)

#create logging
if not app.debug:
    import logging
    from logging import FileHandler
    file_handler = FileHandler('error.log')
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)


#Import routes
import views

#Import error handling
import error
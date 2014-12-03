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
from tinker.wufoo.views import wufoo_blueprint
from tinker.redirects.views import redirect_blueprint
from tinker.heading_upgrade.views import heading_upgrade
app.register_blueprint(event_blueprint, url_prefix='/event')
app.register_blueprint(faculty_bio_blueprint, url_prefix='/faculty-bios')
app.register_blueprint(wufoo_blueprint, url_prefix='/wufoo')
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


@app.route('/peanut')
def peanut():
    from flask import render_template
    return render_template('peanut.html')


@app.route('/peanut/fact', methods=['GET', 'POST'])
def get_peanut_fact():
    import random
    from flask import jsonify
    facts = [
        'It takes about 540 peanuts to make a 12-ounce jar of peanut butter.',
        'Delta Airlines purchased 69.6 million packs of peanuts for its passengers in 2013',
        'By law, any product labeled "peanut butter" in the United States must be at least 90 percent peanuts.',
        'Four of the top 10 candy bars manufactured in the USA contain peanuts or peanut butter.',
        'Americans spend almost $800 million a year on peanut butter.',
        'Peanuts are the #1 snack nut consumed in the U.S., accounting for two-thirds of the snack nut market.',
        'The average American consumes more than six pounds of peanuts and peanut butter products each year.',
        'The amount of peanut butter eaten in a year could wrap the earth in a ribbon of 18-ounce peanut butter jars one and one-third times.',
        'Adrian Finch of Australia holds the Guinness World Record for peanut throwing, launching the lovable legume 111 feet and 10 inches in 1999 to claim the record.',
        'The Guiness Book of World Records reports that on April 3, 1973, Chris Ambrose, Clerkenwell, London, ate 100 peanuts singly in 59.2 seconds!',
        "In August 1976, Tom Miller, a University of Colorado student, pushed a peanut to the top of Pike's Peak with his nose(14,100 feet!). It took him 4 days, 23 hours,47 minutes and 3 seconds.",
        'September 13th is National Peanut Day.',
        "Archibutyrophobia (pronounced A'-ra-kid-bu-ti-ro-pho-bi-a) is the fear of getting peanut butter stuck to the roof of your mouth."
    ]
    return jsonify({'fact': (random.choice(facts))})


@app.route('/cache-test/<path:img_path>')
@app.route('/cache-test')
def cache_test(img_path=None):
    if not img_path:
        img_path = '/academics/faculty/images/lundberg-kelsey.jpg'
    return tools.clear_image_cache(img_path)

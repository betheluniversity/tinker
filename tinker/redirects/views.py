__author__ = 'ejc84332'

from flask import Blueprint, render_template, abort
from flask.ext.sqlalchemy import SQLAlchemy

from tinker import app, db

from tinker.redirects.models import BethelRedirect

redirect_blueprint = Blueprint('redirect_blueprint', __name__,
                               template_folder='templates')


@redirect_blueprint.route('/')
def show():

    redirects = BethelRedirect.query.all()

    return render_template('redirects.html', **locals())
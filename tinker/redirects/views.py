__author__ = 'ejc84332'

from flask import Blueprint, render_template, abort, request
from flask.ext.sqlalchemy import SQLAlchemy

from tinker import app, db

from tinker.redirects.models import BethelRedirect

redirect_blueprint = Blueprint('redirect_blueprint', __name__,
                               template_folder='templates')


@redirect_blueprint.route('/')
def show():

    redirects = BethelRedirect.query.all()

    return render_template('redirects.html', **locals())


@redirect_blueprint.route('/new-redirect-submit', methods=['post'])
def new_redirect_submti():

    form = request.form
    from_path = form['new-redirect-from']
    to_url = form['new-redirect-to']
    redirect = BethelRedirect(from_path=from_path, to_url=to_url)

    db.session.add(redirect)
    db.session.commit()


@redirect_blueprint.route('/load-redirects')
def load_redirects():

    ret = ""

    redirects = BethelRedirect.query.all()

    # for redirect in redirects:
    #     ret += "<tr>"
    #     ret += "<td>" + redirect.from_path + "</td>"
    #     ret += "<td>" + redirect.to_url + "</td>"
    #     ret += "</tr>"
    #
    # return ret

    return render_template('redirect-ajax.html', **locals())
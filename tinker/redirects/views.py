__author__ = 'ejc84332'

#python
import re
import smtplib

from flask import Blueprint, render_template, abort, request, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Session
from BeautifulSoup import BeautifulSoup

from tinker import app, db, tools

from tinker.redirects.models import BethelRedirect

redirect_blueprint = Blueprint('redirect_blueprint', __name__,
                               template_folder='templates')


def check_redirect_groups():
    groups = tools.get_groups_for_user()
    if 'Tinker Redirects' not in groups:
        abort(403)


@redirect_blueprint.route('/')
def show():
    check_redirect_groups()
    redirects = BethelRedirect.query.all()

    return render_template('redirects.html', **locals())


@redirect_blueprint.route('/search', methods=['post'])
def search():
    check_redirect_groups()
    #todo: limit results to...100?
    from_path = request.form['from_path'] + "%"

    if from_path == "%":
        return ""

    redirects = BethelRedirect.query.filter(BethelRedirect.from_path.like(from_path)).limit(100).all()
    redirects.sort()
    return render_template('redirect-ajax.html', **locals())


@redirect_blueprint.route('/new-submit', methods=['post'])
def new_redirect_submti():
    check_redirect_groups()
    form = request.form
    from_path = form['new-redirect-from']
    to_url = form['new-redirect-to']

    if not from_path.startswith("/"):
        from_path = "/" + from_path

    redirect = BethelRedirect(from_path=from_path, to_url=to_url)

    db.session.add(redirect)
    db.session.commit()

    ##Update the file after every submit?
    create_redirect_text_file()

    return str(redirect)


@redirect_blueprint.route('/api-submit', methods=['get', 'post'])
def new_api_submit():
    body = request.form['body']

    soup = BeautifulSoup(body)
    all_text = ''.join(soup.findAll(text=True))
    redirects = re.findall("(redirect: \S* \S*)", all_text)
    redirect = ""
    for line in redirects:
        try:
            line = line.lstrip().rstrip()
            if line.startswith('redirect:'):
                line = line.replace('redirect:', '').lstrip().rstrip()
                from_url, to_url = line.split()
                from_path = from_url.replace("www.bethel.edu", "").replace("http://", "").replace('https://', "")
                redirect = BethelRedirect(from_path=from_path, to_url=to_url)
                db.session.add(redirect)
                db.session.commit()
        except:
            message = "redirect from %s to %s already exists" % (from_url, to_url)
            sender = 'tinker@bethel.edu'
            receivers = ['e-jameson@bethel.edu', 'a-vennerstrom@bethel.edu']

            smtpObj = smtplib.SMTP('localhost')
            smtpObj.sendmail(sender, receivers, message)
            print "Successfully sent email"
            db.session.rollback()
            return "sent email notice"

    if redirect:
        create_redirect_text_file()
    return str(redirect)


@redirect_blueprint.route('/delete', methods=['post'])
def delete_redirect():
    check_redirect_groups()
    path = request.form['from_path']

    resp = str(path)

    try:
        redirect = BethelRedirect.query.get(path)
        db.session.delete(redirect)
        db.session.commit()
        resp = create_redirect_text_file()

    except:
        return "fail"

    return "deleted %s" % resp


@redirect_blueprint.route('/compile')
def compile_redirects():
    check_redirect_groups()
    resp = create_redirect_text_file()
    return resp


def create_redirect_text_file():

    map_file = open(app.config['REDIRECT_FILE_PATH'], 'w')
    map_file_back = open(app.config['REDIRECT_FILE_PATH'] + ".back", 'w')
    redirects = BethelRedirect.query.all()

    for item in redirects:
        map_file.write("%s %s\n" % (item.from_path, item.to_url))
        map_file_back.write("%s %s\n" % (item.from_path, item.to_url))

    resp = 'done'
    return resp


@redirect_blueprint.route('/test')
def test():
    redirects = BethelRedirect.query.all()
    resp = ["<pre>"]
    for redirect in redirects:

        from_path = redirect.from_path
        to_url = redirect.to_url

        if 'bethel.edu' not in to_url:
            continue
        try:
            to_path = to_url.split('.edu')[1]
        except:
            x = 2
        if from_path == to_path:
            db.session.delete(redirect)
            db.session.commit()
            resp.append("deleted %s : %s" % (from_path, to_path))

    create_redirect_text_file()
    resp.append("</pre>")
    return '\n'.join(resp)


# @redirect_blueprint.route('/load')
# def load_redirects():
#
#     from sqlalchemy.exc import IntegrityError
#
#     url_file = open('/Users/ejc84332/Desktop/www-host.txt.map', 'r')
#     lines = [line.strip() for line in url_file.readlines()]
#
#     for line in lines:
#         if line.startswith("#") or line == "\n" or line == "":
#             continue
#         try:
#             from_path, to_url = line.split()
#             redirect = BethelRedirect(from_path=from_path, to_url=to_url)
#             db.session.add(redirect)
#             db.session.commit()
#         except IntegrityError:
#             db.session.rollback()
#
#
#     return "done"
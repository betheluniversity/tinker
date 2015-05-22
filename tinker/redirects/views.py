__author__ = 'ejc84332'

# python
import re
import smtplib
import datetime

# flask
from flask import Blueprint, render_template, abort, request
from BeautifulSoup import BeautifulSoup

# tinker
from tinker import app, db, tools
from tinker.redirects.models import BethelRedirect

redirect_blueprint = Blueprint('redirect_blueprint', __name__, template_folder='templates')


def check_redirect_groups():
    groups = tools.get_groups_for_user()
    if 'Tinker Redirects' not in groups:
        abort(403)


@redirect_blueprint.route('/expire')
def delete_expired_redirects():
    today = datetime.datetime.utcnow()
    redirects = BethelRedirect.query.filter(BethelRedirect.expiration_date < today).all()
    for redirect in redirects:
        db.session.delete(redirect)
    db.session.commit()
    create_redirect_text_file()
    return 'done'


@redirect_blueprint.route('/')
def show():
    check_redirect_groups()
    redirects = BethelRedirect.query.all()

    return render_template('redirects.html', **locals())


@redirect_blueprint.route('/search', methods=['post'])
def search():
    check_redirect_groups()
    # todo: limit results to...100?
    search_type = request.form['type']
    search_query = request.form['search'] + "%"

    if search == "%" or search_type not in ['from_path', 'to_url']:
        return ""

    if search_type == 'from_path':
        redirects = BethelRedirect.query.filter(BethelRedirect.from_path.like(search_query)).limit(100).all()
    else:
        redirects = BethelRedirect.query.filter(BethelRedirect.to_url.like(search_query)).limit(100).all()
    redirects.sort()
    return render_template('redirect-ajax.html', **locals())


@redirect_blueprint.route('/new-submit', methods=['post'])
def new_redirect_submit():
    check_redirect_groups()
    form = request.form
    from_path = form['new-redirect-from']
    to_url = form['new-redirect-to']
    short_url = form.get('short-url') == 'on'
    expiration_date = form.get('expiration-date')

    if expiration_date:
        expiration_date = datetime.datetime.strptime(expiration_date, "%a %b %d %Y")
    else:
        expiration_date = None

    if not from_path.startswith("/"):
        from_path = "/%s" % from_path

    redirect = BethelRedirect(from_path=from_path, to_url=to_url, short_url=short_url, expiration_date=expiration_date)

    db.session.add(redirect)
    db.session.commit()

    # Update the file after every submit?
    create_redirect_text_file()

    return str(redirect)


@redirect_blueprint.route('/public/api-submit', methods=['get', 'post'])
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
            receivers = ['e-jameson@bethel.edu', 'a-vennerstrom@bethel.edu', 'ces55739@bethel.edu']
            
            smtp_obj = smtplib.SMTP('localhost')
            smtp_obj.sendmail(sender, receivers, message)
            print "Successfully sent email"
            db.session.rollback()
            return "sent email notice"

    if redirect:
        create_redirect_text_file()
    return str(redirect)


@redirect_blueprint.route('/new-internal-submit/<from_path>/<to_url>', methods=['post', 'get'])
def new_internal_redirect_submit(from_path, to_url):
    app.logger.warn(": Correctly called the function")
    # added logic to have Tinker be able to internally create a redirect
    check_redirect_groups()

    if not from_path.startswith("/"):
        from_path = "/%s" % from_path

    # if one from the current from exists, remove it.
    try:
        redirect = BethelRedirect.query.get(from_path)
        db.session.delete(redirect)
        db.session.commit()
        resp = create_redirect_text_file()
        app.logger.warn(": Correctly deleted if necessary")
    except:
        print "no deletion was made"

    # create the redirect
    try:
        redirect = BethelRedirect(from_path=from_path, to_url=to_url)
        db.session.add(redirect)
        db.session.commit()
        print "Successfully created a internal redirect"
        app.logger.warn(": Correctly created a new one")
    except:
        db.session.rollback()

    # Update the file after every submit?
    create_redirect_text_file()

    app.logger.warn(": Correctly finished")
    return str(redirect)


@redirect_blueprint.route('/public/api-submit-asset-expiration', methods=['get', 'post'])
def new_api_submit_asset_expiration():
    subject = request.form['subject']
    soup = BeautifulSoup(subject)
    all_text = ''.join(soup.findAll(text=True))

    try:
        lines = all_text.split("Asset expiration notice for Public:")
        from_path = "/" + lines[1].lstrip().rstrip()
        to_url = "https://www.bethel.edu/employment/openings/postings/job-closed"
        redirect = BethelRedirect(from_path=from_path, to_url=to_url)
        db.session.add(redirect)
        db.session.commit()
    except:
        message = "redirect from %s to %s already exists" % (from_path, to_url)
        sender = 'tinker@bethel.edu'
        receivers = ['ces55739@bethel.edu']

        smtp_obj = smtplib.SMTP('localhost')
        smtp_obj.sendmail(sender, receivers, message)
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


@redirect_blueprint.route('/thumbor-clear')
def clear_thumbor():
    check_redirect_groups()
    try:
        tools.clear_image_cache()
        return "success"
    except:
        return "error"


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

__author__ = 'ejc84332'

import re
import smtplib
from datetime import datetime

from BeautifulSoup import BeautifulSoup
from flask import Blueprint, render_template, request, abort, session
from flask.ext.classy import FlaskView, route
from flask.ext.wtf import Form

from tinker import db, app
from tinker.admin.redirects.redirects_controller import RedirectsController
from tinker.admin.redirects.models import BethelRedirect

RedirectsBlueprint = Blueprint('redirects', __name__, template_folder='templates')


class RedirectsView(FlaskView):
    route_base = '/admin/redirect'

    def __init__(self):
        self.base = RedirectsController()

    # This method is called before a request is made
    def before_request(self, name, **kwargs):
        # Checks to see what group the user is in
        if 'Tinker Redirects' not in session['groups']:
            abort(403)

    # Redirects homepage
    def index(self):
        redirects = BethelRedirect.query.all()
        form = Form()
        return render_template('redirects.html', **locals())

    # Deletes the chosen redirect
    @route("/delete", methods=['post'])
    def delete_redirect(self):
        path = request.form['from_path']
        try:
            redirect = BethelRedirect.query.get(path)
            self.base.database_delete(redirect)
            resp = self.base.create_redirect_text_file()

        except:
            return "fail"
        return "deleted %s" % resp

    # Finds all redirects associated with the from path entered
    @route("/search", methods=['post'])
    def search(self):
        # todo: limit results to...100?
        search_type = request.form['type']
        search_query = request.form['search'] + "%"
        if self.search == "%" or search_type not in ['from_path', 'to_url']:
            return ""
        if search_type == 'from_path':
            redirects = BethelRedirect.query.filter(BethelRedirect.from_path.like(search_query)).limit(100).all()
        else:
            redirects = BethelRedirect.query.filter(BethelRedirect.to_url.like(search_query)).limit(100).all()
        redirects.sort()
        return render_template('redirect-ajax.html', **locals())

    # Saves the new redirect created
    @route("/new-redirect-submit", methods=['post'])
    def new_redirect_submit(self):
        print "Test method"
        form = request.form
        from_path = form['new-redirect-from']
        to_url = form['new-redirect-to']
        short_url = form.get('short-url') == 'on'
        expiration_date = form.get('expiration-date')

        if expiration_date:
            expiration_date = datetime.strptime(expiration_date, "%a %b %d %Y")
        else:
            expiration_date = None

        if not from_path.startswith("/"):
            from_path = "/%s" % from_path

        try:
            redirect = BethelRedirect(from_path=from_path, to_url=to_url, short_url=short_url,
                                      expiration_date=expiration_date)
            self.base.database_add(redirect)
            # Update the file after every submit?
            self.base.create_redirect_text_file()
        except:
            # Currently we are unable to track down why multiple redirects are being created. This causes this error:
            # (IntegrityError) column from_path is not unique u'INSERT INTO bethel_redirect (from_path, to_url,
            # short_url, expiration_date)
            # Our work around is to just ignore the issue.
            # hopefully this will catch the error.
            db.session.rollback()
            return ""

        return str(redirect)

    # Updates the redirect text file upon request
    def compile(self):
        resp = self.base.create_redirect_text_file()
        return resp

    # Deletes expired redirects on the day of its expiration date
    def expire(self):
        today = datetime.utcnow()
        redirects = BethelRedirect.query.filter(BethelRedirect.expiration_date < today).all()
        for redirect in redirects:
            db.session.delete(redirect)
        db.session.commit()
        self.base.create_redirect_text_file()
        return 'done'

    # This creates redirects generically from a google script and the webmaster email box
    @route('/public/api-submit', methods=['get', 'post'])
    def new_api_submit(self):
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
                    self.base.database_add(redirect)
            except:
                db.session.rollback()

        if redirect:
            self.base.create_redirect_text_file()
        return str(redirect)

    # This creates a redirect for job postings from a google script and the webmaster email box
    @route('/public/api-submit-asset-expiration', methods=['get', 'post'])
    def new_api_submit_asset_expiration(self):
        from_path = ''
        to_url = ''
        subject = request.form['subject']
        soup = BeautifulSoup(subject)
        all_text = ''.join(soup.findAll(text=True))

        try:
            lines = all_text.split("Asset expiration notice for Public:")
            from_path = "/" + lines[1].lstrip().rstrip()
            to_url = "https://www.bethel.edu/employment/openings/postings/job-closed"
            redirect = BethelRedirect(from_path=from_path, to_url=to_url)
            self.base.database_add(redirect)

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
            self.base.create_redirect_text_file()

        return str(redirect)

    @route('/new-internal-submit/<from_path>/<to_url>', methods=['post', 'get'])
    def new_internal_redirect_submit(self, from_path, to_url):
        if not from_path.startswith("/"):
            from_path = "/%s" % from_path

        # if one from the current from exists, remove it.
        try:
            redirect = BethelRedirect.query.get(from_path)
            db.session.delete(redirect)
            db.session.commit()
            # todo not sure if next line is needed
            resp = self.base.create_redirect_text_file()
            app.logger.debug(": Correctly deleted if necessary")
        except:
            redirect = None
            print "no deletion was made"

        # create the redirect
        try:
            redirect = BethelRedirect(from_path=from_path, to_url=to_url)
            db.session.add(redirect)
            db.session.commit()
            print "Successfully created a internal redirect"
            app.logger.debug(": Correctly created a new one")
        except:
            db.session.rollback()

        # Update the file after every submit?
        self.base.create_redirect_text_file()

        app.logger.debug(": Correctly finished")
        return str(redirect)

RedirectsView.register(RedirectsBlueprint)

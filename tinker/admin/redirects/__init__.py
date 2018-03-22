# Global
import re
import requests
import smtplib
import time
from datetime import datetime

# Packages
from BeautifulSoup import BeautifulSoup
from flask import Blueprint, render_template, request, abort, session, Response, stream_with_context
from flask_classy import FlaskView, route

# Local
from tinker import app, db
from tinker.admin.redirects.redirects_controller import RedirectsController
from tinker.tinker_controller import requires_auth
from tinker.tinker_controller import admin_permissions
RedirectsBlueprint = Blueprint('redirects', __name__, template_folder='templates')


class RedirectsView(FlaskView):
    route_base = '/admin/redirect'

    def __init__(self):
        self.base = RedirectsController(db)

    # This method is called before a request is made
    def before_request(self, name, **kwargs):
        admin_permissions(self)

    # Redirects homepage
    def index(self):
        redirects = self.base.get_all_rows()
        return render_template('admin/redirects/home.html', **locals())

    # Deletes the chosen redirect
    @route("/delete", methods=['post'])
    def delete_redirect(self):
        rform = self.base.dictionary_encoder.encode(request.form)
        redirect_id = rform['redirect_id']
        try:
            self.base.delete_row_from_db(redirect_id)
            resp = self.base.create_redirect_text_file()
        except:
            return "fail"
        return "deleted %s" % resp

    # Finds all redirects associated with the from path entered
    @route("/search", methods=['post'])
    def search(self):
        rform = self.base.dictionary_encoder.encode(request.form)
        search_type = rform['type']
        search_query = rform['search']
        if search_query == "%" or search_type not in ['from_path', 'to_url'] or search_query is None:
            return ""
        redirects = self.base.search_db(search_type, search_query)
        return render_template('admin/redirects/ajax.html', **locals())

    # Saves the new redirect created
    @route("/new-redirect-submit", methods=['post'])
    def new_redirect_submit(self):
        form = self.base.dictionary_encoder.encode(request.form)
        from_path = form['new-redirect-from']
        to_url = form['new-redirect-to']
        short_url = form.get('new-redirect-short-url') == 'true'
        expiration_date = form.get('expiration-date')

        if expiration_date:
            expiration_date = datetime.strptime(expiration_date, "%a %b %d %Y")
        else:
            expiration_date = None

        if from_path is None or to_url is None:
            return abort(400)

        if not from_path.startswith("/"):
            from_path = "/%s" % from_path
        try:
            new_redirect = self.base.add_row_to_db(from_path, to_url, short_url, expiration_date)
            # Update the file after every submit?
            self.base.create_redirect_text_file()
            return str(new_redirect)
        except:
            # Currently we are unable to track down why multiple redirects are being created. This causes this error:
            # (IntegrityError) column from_path is not unique u'INSERT INTO bethel_redirect (from_path, to_url,
            # short_url, expiration_date)
            # Our work around is to just ignore the issue.
            # hopefully this will catch the error.
            self.base.rollback()
            return ""

    # Updates the redirect text file upon request
    def compile(self):
        resp = self.base.create_redirect_text_file()
        return resp

    def marcel(self, key):
        """ Load new redirects from a Marcel spreadhseet."""
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        # from sqlite3 import IntegrityError
        scope = ['https://spreadsheets.google.com/feeds']

        credentials = ServiceAccountCredentials.from_json_keyfile_name(app.config['GSPREAD_CONFIG'], scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open_by_key(key).worksheet("redirects")

        for i, row in enumerate(worksheet.get_all_values()):
            if i > 0:
                from_url = row[0].split("bethel.edu")[1]
                to_url = row[1]

                try:
                    self.base.add_row_to_db(from_url, to_url, None, None)
                except Exception as e:
                    # redirect already exists
                    self.base.rollback()
                    print e
                    continue
            done_cell = "C%s" % str(i + 1)
            worksheet.update_acell(done_cell, 'x')
            time.sleep(1)
            print(i)

        return "done"

    def marcel_check(self, key):
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        # from sqlite3 import IntegrityError
        scope = ['https://spreadsheets.google.com/feeds']

        credentials = ServiceAccountCredentials.from_json_keyfile_name(app.config['GSPREAD_CONFIG'], scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open_by_key(key).worksheet("redirects")

        bad = 0
        for i, row in enumerate(worksheet.get_all_values()):
            if i > 0:
                from_url = row[0].split("bethel.edu")[1]
                from_url = 'https://www.bethel.edu%s' % from_url
                r = requests.get(from_url, allow_redirects=False)
                if r.status_code != 301:
                    print "found bad line (%s): %s" % (i, from_url)
                    bad += 1
        return "done. Found %s bad lines" % bad

    # Deletes expired redirects on the day of its expiration date
    @requires_auth
    @route('/public/expire', methods=['get'])
    def expire(self):
        self.base.expire_old_redirects()
        self.base.create_redirect_text_file()
        return 'done'

    # This creates redirects generically from a google script and the webmaster email box
    @requires_auth
    @route('/public/api-submit', methods=['post'])  # ['get', 'post'])
    def new_api_submit(self):
        rform = self.base.dictionary_encoder.encode(request.form)
        body = rform['body']

        soup = BeautifulSoup(body)
        all_text = ''.join(soup.findAll(text=True))
        redirects = re.findall("(redirect: \S* \S*)", all_text)
        redirect = None
        for line in redirects:
            try:
                line = line.lstrip().rstrip()
                if line.startswith('redirect:'):
                    line = line.replace('redirect:', '').lstrip().rstrip()
                    from_url, to_url = line.split()
                    from_path = from_url.replace("www.bethel.edu", "").replace("http://", "").replace('https://', "")
                    redirect = self.base.api_add_row(from_path, to_url)
            except:
                self.base.rollback()

        if redirect:
            self.base.create_redirect_text_file()
        return str(redirect)

    # This creates a redirect for job postings from a google script and the webmaster email box
    @requires_auth
    @route('/public/api-submit-asset-expiration', methods=['get', 'post'])
    def new_api_submit_asset_expiration(self):
        rform = self.base.dictionary_encoder.encode(request.form)
        from_path = ''
        to_url = ''
        subject = rform['subject']
        soup = BeautifulSoup(subject)
        all_text = ''.join(soup.findAll(text=True))

        try:
            lines = all_text.split("Asset expiration notice for Public:")
            from_path = "/" + lines[1].lstrip().rstrip()
            to_url = "https://www.bethel.edu/employment/openings/postings/job-closed"
            redirect = self.base.api_add_row(from_path, to_url)

        except:
            message = "redirect from %s to %s already exists" % (from_path, to_url)
            sender = 'tinker@bethel.edu'
            receivers = app.config['ADMINS']

            smtp_obj = smtplib.SMTP('localhost')
            smtp_obj.sendmail(sender, receivers, message)
            print "Successfully sent email"
            self.base.rollback()
            return "sent email notice"

        if redirect:
            self.base.create_redirect_text_file()

        return str(redirect)

    @requires_auth
    @route('/public/new-internal-submit/<from_path>/<to_url>', methods=['post', 'get'])
    def new_internal_redirect_submit(self, from_path, to_url):
        if not from_path.startswith("/"):
            from_path = "/%s" % from_path

        redirect = ""
        # if one from the current from exists, remove it.
        try:
            self.base.delete_row_from_db(from_path)
            # todo not sure if next line is needed
            resp = self.base.create_redirect_text_file()
            app.logger.debug(": Correctly deleted if necessary")
        except:
            redirect = None
            print "no deletion was made"

        # create the redirect
        try:
            redirect = self.base.api_add_row(from_path, to_url)
            print "Successfully created a internal redirect"
            app.logger.debug(": Correctly created a new one")
        except:
            self.base.rollback()

        # Update the file after every submit?
        self.base.create_redirect_text_file()

        app.logger.debug(": Correctly finished")
        return str(redirect)

    @requires_auth
    @route('/public/clear-redirects')
    def redirect_clear(self):
        # return "Test"
        return self.base.redirect_change()

RedirectsView.register(RedirectsBlueprint)

# local
from datetime import datetime
import urllib
import requests
from redirect_domains import redirect_domains

# Packages
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, session
from requests.exceptions import SSLError, ConnectionError
from urllib3.exceptions import ProtocolError, MaxRetryError
from sqlalchemy import and_

# tinker
from tinker import app
from tinker.admin.redirects.models import BethelRedirect
from tinker.tinker_controller import TinkerController


class RedirectsController(TinkerController):
    def __init__(self, database):
        super(RedirectsController, self).__init__()
        if isinstance(database, SQLAlchemy):
            self.db = database
        else:
            raise TypeError('tinker/admin/redirects/redirects_controller requires that the database arg is SQLAlchemy')

    # Creates a new redirect text file
    def create_redirect_text_file(self):
        redirect_domain_list = redirect_domains
        files = {}
        redirects = BethelRedirect.query.all()

        for domain in redirect_domain_list:
            files[domain] = open(app.config['REDIRECTS_FOLDER_PATH'] + '/' + domain + '.txt', 'w')

        for item in redirects:
            for domain in redirect_domain_list:
                if domain == item.domain:
                    files[domain].write("%s %s\n" % (item.from_path, item.to_url))

        return 'done'

    def add_row_to_db(self, from_path, to_url, short_url, expiration_date, username=None, domain="www.bethel.edu"):
        if from_path == '/':
            return False

        if not username:
            username = session["username"]

        new_redirect = BethelRedirect(domain=domain, from_path=from_path, to_url=to_url, short_url=short_url,
                                      expiration_date=expiration_date, username=username)
        self.db.session.add(new_redirect)
        self.db.session.commit()
        return new_redirect

    def api_add_row(self, from_path, to_url):
        new_redirect = BethelRedirect(username="API-Generated", from_path=from_path, to_url=to_url)
        self.db.session.add(new_redirect)
        self.db.session.commit()
        return new_redirect

    def search_db(self, redirect_from_path, redirect_to_url):
        if redirect_from_path == "" and redirect_to_url == "":
            return ""
        results = BethelRedirect.query.filter(and_(BethelRedirect.from_path.like(redirect_from_path + '%'),
                                                   BethelRedirect.to_url.like('%' + redirect_to_url + '%'))).limit(100).all()
        results.sort()
        return results

    def delete_row_from_db(self, id):
        redirect_to_delete = BethelRedirect.query.filter(BethelRedirect.id.like(id)).limit(1).one()
        self.db.session.delete(redirect_to_delete)
        self.db.session.commit()

    def expire_old_redirects(self):
        today = datetime.utcnow()
        redirects = BethelRedirect.query.filter(BethelRedirect.expiration_date < today).all()
        for redirect in redirects:
            self.db.session.delete(redirect)
        self.db.session.commit()

    def get_all_rows(self):
        return BethelRedirect.query.all()

    def rollback(self):
        self.db.session.rollback()

    def paths_are_valid(self, from_path, to_url):
        if not from_path or from_path == '/' or not to_url:
            return False
        return True

    def redirect_change(self):

        redirects = BethelRedirect.query.all()

        changed = []
        deleted = []

        for redirect in redirects:
            try:
                response = requests.get('https://www.bethel.edu' + redirect.from_path, verify=False)
                redirect.to_url.replace('\n', '')
                redirect.to_url.replace(' ', '')

            except SSLError as e:  # .SSLError and .CertificateError caught here
                continue

            except ConnectionError as e:  # MaxRetry and ProtocolError are being thrown here

                if 'Max retries exceeded' in e.args[0].args[0]:  # MaxRetryError caught here and marked for deletion

                    deleted.append({'from_path': redirect.from_path, 'to_url': redirect.to_url})
                    continue

                else:  # If it passes the other logic, its a protocol error
                    continue

            except:  # Needs to be here to catch the rest of the hiccups in the redirects
                continue

            if response.url != redirect.to_url:

                if 'auth' in response.url:  # if auth is in the response.url, its decoded
                    response.url = urllib.unquote(urllib.unquote(response.url))
                    redirect.query.filter_by(from_path=redirect.from_path).update(dict(to_url=response.url))
                    self.db.session.commit()
                    continue

                redirect.query.filter_by(from_path=redirect.from_path).update(dict(to_url=response.url))
                self.db.session.commit()
                changed.append({'to_url': redirect.to_url, 'response': response.url})

        return render_template('admin/redirects/clear-redirects.html', **locals())

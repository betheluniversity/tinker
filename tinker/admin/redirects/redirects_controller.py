
# local
from datetime import datetime
import urllib
import requests

# Packages
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from requests.exceptions import SSLError, ConnectionError
from urllib3.exceptions import ProtocolError, MaxRetryError

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
        map_file = open(app.config['REDIRECTS_FILE_PATH'], 'w')
        map_file_back = open(app.config['REDIRECTS_FILE_PATH'] + ".back", 'w')
        redirects = BethelRedirect.query.all()

        for item in redirects:
            map_file.write("%s %s\n" % (item.from_path, item.to_url))
            map_file_back.write("%s %s\n" % (item.from_path, item.to_url))

        return 'done'

    def add_row_to_db(self, from_path, to_url, short_url, expiration_date):
        if from_path == '/':
            return False

        new_redirect = BethelRedirect(from_path=from_path, to_url=to_url, short_url=short_url,
                                      expiration_date=expiration_date)
        self.db.session.add(new_redirect)
        self.db.session.commit()
        return new_redirect

    def api_add_row(self, from_path, to_url):
        new_redirect = BethelRedirect(from_path=from_path, to_url=to_url)
        self.db.session.add(new_redirect)
        self.db.session.commit()
        return new_redirect

    def search_db(self, search_type, term):
        term += "%"
        if search_type == "from_path":  # Search by from_path
            results = BethelRedirect.query.filter(BethelRedirect.from_path.like(term)).limit(100).all()
        else:  # Search by to_url
            results = BethelRedirect.query.filter(BethelRedirect.to_url.like(term)).limit(100).all()
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
                    # creates a new redirect to replace the old one after deleting
                    redirect.update(from_path=redirect.from_path, to_url=response.url,
                                    short_url=redirect.short_url,
                                    expiration_date=redirect.expiration_date)
                    self.db.session.commit()
                    continue

                # checks if the changes are redundant (adding '/' or changing 'http' > 'https')
                if 'https' not in redirect.to_url:
                    https_test = redirect.to_url.replace('http', 'https')
                    if response.url == https_test:
                        # Creates a new redirect to replace the old one after deleting
                        redirect.update(from_path=redirect.from_path, to_url=response.url,
                                        short_url=redirect.short_url,
                                        expiration_date=redirect.expiration_date)
                        self.db.session.commit()
                        continue
                elif response.url == redirect.to_url + '/':
                    # creates a new redirect to replace the old one after deleting
                    redirect.update(from_path=redirect.from_path, to_url=response.url,
                                    short_url=redirect.short_url,
                                    expiration_date=redirect.expiration_date)
                    self.db.session.commit()
                    continue

                redirect.update(from_path=redirect.from_path, to_url=response.url,
                                short_url=redirect.short_url,
                                expiration_date=redirect.expiration_date)
                self.db.session.commit()
                changed.append({'to_url': redirect.to_url, 'response': response.url})

        return render_template('admin/redirects/clear-redirects.html', **locals())

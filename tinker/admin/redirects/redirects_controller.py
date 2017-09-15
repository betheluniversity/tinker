import requests

from datetime import datetime
from httplib import InvalidURL

from flask_sqlalchemy import SQLAlchemy

# tinker
from requests.exceptions import SSLError, ConnectionError

# Global
from datetime import datetime

# Packages
from flask_sqlalchemy import SQLAlchemy

# Local
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

    # TODO: PG, 7/6/17: I can't find where this method is used
    def get_model(self):
        return self.db.Model

    def add_row_to_db(self, from_path, to_url, short_url, expiration_date):
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

    def delete_row_from_db(self, from_path):
        redirect_to_delete = BethelRedirect.query.get(from_path)
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
        # import urllib2
        # from urllib2 import addinfourl, URLError

        redirects = BethelRedirect.query.all()
        for row in redirects:
            try:
                response = requests.get('https://www.bethel.edu' + row.from_path)
                row.to_url.replace('\n', '')
                row.to_url.replace(' ', '')
            except SSLError:
                # Throws SSLError for an unknown reason, skipping it because we can't create the response object
                continue
            except ConnectionError:  # TODO come back to this error
                continue
            except:
                pass

            if response.url != row.to_url:
                yield 'changing %s to %s <br/>' % (row.to_url, response.url)
                # redirects.replace(row.to_url, response.url)

    # def update_redirect_file(self):
    #     changes = open('/Users/bak45247/Desktop/RedirectChanges.txt', 'r+')
    #     to_write = ''
    #     write_changes = ''
    #     counter = 0
    #     import urllib2
    #     from urllib2 import addinfourl, URLError
    #     with open(app.config['REDIRECTS_FILE_PATH']) as redirects:
    #         for line in redirects:
    #             counter += 1
    #             if counter < 850:
    #                 continue
    #             try:
    #                 from_path, to_url = line.split(' ')
    #                 to_url = to_url.replace('\n', '')
    #             except ValueError:
    #                 yield line + 'ValueError <br/>'
    #                 continue
    #
    #             try:
    #                 response = urllib2.urlopen('https://www.bethel.edu' + from_path)
    #             except URLError, e:
    #                 yield line + 'URLError <br/>'
    #                 print e.args
    #                 continue
    #             except InvalidURL:
    #                 yield line + 'InvalidURL <br/>'
    #                 continue
    #
    #             path = response.geturl()
    #
    #             if response.getcode() == 404:
    #                 write_changes += 'deleted path' + from_path + '<br/>'
    #                 continue
    #
    #             if '/oops' in to_url:
    #                 print "this from_path '%s' goes to oops %s" % (from_path, to_url)
    #                 continue
    #
    #             elif to_url != path:
    #                 write_changes += 'changed to_url ' + to_url + ' to ' + path + '<br/>'
    #                 to_url = path
    #
    #             to_write += from_path + ' ' + to_url + '\n'
    #
    #             # prints every thousandth line, if it skips a thousandth line, that means the redirect either failed or points to oops
    #             if counter % 100 == 0:
    #                 yield line + ' line number %s <br/>' % counter
    #
    #         yield '\n' + write_changes
    #     # redirects.write(to_write)
    #     changes.write(write_changes)


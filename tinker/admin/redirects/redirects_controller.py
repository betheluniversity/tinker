# import requests

from datetime import datetime
from httplib import InvalidURL

from flask_sqlalchemy import SQLAlchemy

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

    def update_redirect_file(self):
        redirects = open(app.config['REDIRECTS_FILE_PATH'], 'r+')
        to_write = ''
        write_changes = ''
        counter = 0
        import urllib2
        from urllib2 import addinfourl, URLError
        for line in redirects:
            try:
                from_path, to_url = line.split(' ')
                to_url = to_url.replace('\n', '')
            except ValueError:
                yield '<br/>' + line + 'ValueError'
                continue
            except InvalidURL:
                yield '<br/>' + line + 'InvalidURL'
                continue

            try:
                response = urllib2.urlopen('https://www.bethel.edu' + from_path)
            except URLError:
                continue

            path = response.geturl()

            if response.getcode() == 404:
                # yield "deleted path %s <br/>" % from_path
                write_changes += 'deleted path' + from_path + '<br/>'
                continue

            if '/oops' in to_url:
                print "this from_path %s goes to oops %s" % (from_path, to_url)
                continue

            elif to_url != path:
                # yield "changed to_url %s to %s <br/>" % (to_url, path)
                write_changes += 'changed to_url' + to_url + 'to' + path + '<br/>'
                to_url = path

            to_write += from_path + ' ' + to_url + '\n'

            counter += 1
            if counter % 50 == 0:
                yield '-'

        yield write_changes
        redirects.write(to_write)


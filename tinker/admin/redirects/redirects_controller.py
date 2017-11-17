
# tinker
import urllib

import requests
from requests.exceptions import SSLError, ConnectionError

# Global
from datetime import datetime

# Packages
from flask_sqlalchemy import SQLAlchemy

# Local
from urllib3.exceptions import ProtocolError, MaxRetryError

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

        loop_counter = 0

        redirects = BethelRedirect.query.all()
        # following are files to be written so we can pass the 'change log' over to marketing
        # with this, they can approve or ask us to fix/replace some of the redirects
        checkDelete = open('Check_For_Deletion.html', 'w+')
        changed = open('Redirect_Changed.html', 'w+')
        redundant_changes = open('Redundant_Changes.html', 'w+')

        today = datetime.now()
        today = today.strftime("%m/%d/%y %I:%M")

        # redirects that are being changed (not redundant changes though)
        changed.write('These are the redirects that are being changed. \n' + str(today) + '</br></br>')
        changed.write("""<table>
                        <thead>
                        <tr>
                        <th style = 'text-align: left'> From Path </th>
                        <th style = 'text-align: left'> To Url </th>
                        <th style = 'text-align: left'> Changed to </th>
                        </tr>
                        </thead>
                        <tfoot>""")

        # these redirects will be marked for deletion. keeping them is based on discretion
        checkDelete.write('These are the redirects that are should be looked at for deletion. \n' + str(today) + '</br></br>')
        checkDelete.write("""<table>
                        <thead>
                        <tr>
                        <th style = 'text-align: left'> From Path </th>
                        <th style = 'text-align: left'> To Url </th>
                        </tr>
                        </thead>
                        <tfoot>""")

        # file for redundant changes (adding '/' to the end or only switching 'http' to 'https'
        redundant_changes.write("""<table>
                                    <thead>
                                    <tr>
                                    <th style = 'text-align: left'> From Path </th>
                                    <th style = 'text-align: left'> To Url </th>
                                    <th style = 'text-align: left'> Change </th>
                                    </tr>
                                    </thead>
                                    <tfoot>""")

        for redirect in redirects:
            loop_counter += 1
            if loop_counter % 2000 == 0:
                print loop_counter
            try:
                response = requests.get('https://www.bethel.edu' + redirect.from_path)
                redirect.to_url.replace('\n', '')
                redirect.to_url.replace(' ', '')

            except SSLError as e:  # .SSLError and .CertificateError caught here
                continue

            except ConnectionError as e:  # MaxRetry and ProtocolError are being thrown here

                if 'Max retries exceeded' in e.args[0].args[0]:  # MaxRetryError caught here and marked for deletion

                    yield "Printing to check for deletion: " + redirect.from_path + "<br/>"
                    checkDelete.write("<tr>\n" +
                                    "<td>" + redirect.from_path + "</td>\n"
                                    "<td>" + redirect.to_url + "</td>\n"
                                  "</tr>\n")
                    continue

                else:  # If it passes the other logic, its a protocol error
                    continue

            except:  # Needs to be here to catch the rest of the hiccups in the redirects
                continue

            if response.url != redirect.to_url:

                if 'auth' in response.url:  # if auth is in the response.url, its decoded
                    response.url = urllib.unquote(urllib.unquote(response.url))
                    # creates a new redirect to replace the old one after deleting
                    new_redirect = BethelRedirect(from_path=redirect.from_path, to_url=response.url,
                                                  short_url=redirect.short_url,
                                                  expiration_date=redirect.expiration_date)
                    self.db.session.delete(redirect)
                    self.db.session.add(new_redirect)
                    self.db.session.commit()
                    continue

                # checks if the changes are redundant (adding '/' or changing 'http' > 'https')
                if 'https' not in redirect.to_url:
                    https_test = redirect.to_url.replace('http', 'https')
                    if response.url == https_test:
                        # Creates a new redirect to replace the old one after deleting
                        new_redirect = BethelRedirect(from_path=redirect.from_path, to_url=response.url,
                                                      short_url=redirect.short_url,
                                                      expiration_date=redirect.expiration_date)
                        self.db.session.delete(redirect)
                        self.db.session.add(new_redirect)
                        self.db.session.commit()
                        redundant_changes.write("<tr>\n" +
                                                "<td>" + redirect.from_path + "</td>\n"
                                                "<td>" + redirect.to_url + "</td>\n"
                                                "<td> Changing http to https </td>\n"
                                                "</tr>\n")
                        continue
                elif response.url == redirect.to_url + '/':
                    # creates a new redirect to replace the old one after deleting
                    new_redirect = BethelRedirect(from_path=redirect.from_path, to_url=response.url,
                                                  short_url=redirect.short_url,
                                                  expiration_date=redirect.expiration_date)
                    self.db.session.delete(redirect)
                    self.db.session.delete(redirect)
                    self.db.session.add(new_redirect)
                    self.db.session.commit()
                    redundant_changes.write("<tr>\n" +
                                            "<td>" + redirect.from_path + "</td>\n"
                                            "<td>" + redirect.to_url + "</td>\n"
                                            "<td> Adding '/' at end </td>\n"
                                            "</tr>\n")
                    continue

                yield 'changing %s to %s <br/>' % (redirect.to_url, response.url)
                # [redirects.replace(redirect.to_url, response.url) for item in redirect]
                new_redirect = BethelRedirect(from_path=redirect.from_path, to_url=response.url,
                                              short_url=redirect.short_url,
                                              expiration_date=redirect.expiration_date)
                self.db.session.delete(redirect)
                self.db.session.add(new_redirect)
                self.db.session.commit()
                changed.write("<tr>\n" +
                                "<td>" + redirect.from_path + "</td>\n"
                                "<td>" + redirect.to_url + "</td>\n"
                                "<td>" + response.url + "</td>"
                                "</tr>\n")

        contact_footer = 'If you have any questions/concerns, please contact web services.'

        changed.write('</tfoot></table> \n \n' + contact_footer)
        checkDelete.write('</tfoot></table> \n \n' + contact_footer)
        redundant_changes.write('</tfoot></table>')

        changed.close()
        checkDelete.close()
        redundant_changes.close()

        print 'done'

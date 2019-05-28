# local
import calendar
import math
import time
from datetime import datetime
import urllib
import requests
import socket

# Packages
from flask_sqlalchemy import SQLAlchemy
from flask import render_template, session
from flask_mail import Message, Mail
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
        map_file = open(app.config['REDIRECTS_FILE_PATH'], 'w')
        map_file_back = open(app.config['REDIRECTS_FILE_PATH'] + ".back", 'w')
        redirects = BethelRedirect.query.all()

        for item in redirects:
            map_file.write("%s %s\n" % (item.from_path, item.to_url))
            map_file_back.write("%s %s\n" % (item.from_path, item.to_url))

        return 'done'

    def add_row_to_db(self, from_path, to_url, short_url, expiration_date, username=None):
        if from_path == '/':
            return False

        if not username:
            username = session["username"]

        new_redirect = BethelRedirect(from_path=from_path, to_url=to_url, short_url=short_url,
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
        if not from_path or from_path == '/' or not to_url or '\t' in from_path or '\t' in to_url:
            return False
        return True

    def redirect_change(self):

        redirects = BethelRedirect.query.all()
        mail = Mail(app)

        changed = []
        deleted = []
        counter = 0  # counts the number of redirects done
        total_redirects = len(redirects)  # total number of redirects
        date = datetime.utcnow()
        redirects_per_day = math.ceil(total_redirects / calendar.monthrange(date.year, date.month)[1])  # number of redirects done per day

        # logic to decide calculations for starting and endingpoints
        if date.day == 1:  # if its the first day, we start at zero
            starting_point = 0
            ending_point = starting_point + redirects_per_day + 5
        elif date.day == calendar.monthrange(date.year, date.month)[1]:  # if its the last day, end at total_redirects
            starting_point = date.day * redirects_per_day - 5
            ending_point = total_redirects
        else:  # otherwise, start 5 before expected beginning and end 5 after the expected ending
            starting_point = date.day * redirects_per_day - 5
            ending_point = starting_point + redirects_per_day + 10

        for redirect in redirects:
            if starting_point <= counter < ending_point:
                try:
                    time.sleep(1)
                    response = self.tinker_requests('https://www.bethel.edu' + redirect.from_path, verify=False)
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

                    changed.append({'to_url': redirect.to_url, 'response': response.url})
                    redirect.query.filter_by(from_path=redirect.from_path).update(dict(to_url=response.url))
                    self.db.session.commit()
            elif counter > ending_point:
                break
            counter += 1

        if changed or deleted:
            if app.config['ENVIRON'] != 'prod':
                print render_template('admin/redirects/clear-redirects.html', **locals())
            else:
                msg = Message(subject='Redirects Changes',
                              sender='noreply@bethel.edu',
                              recipients='bak45247@bethel.edu')
                msg.html = render_template('admin/redirects/clear-redirects.html', **locals())
                mail.send(msg)
        else:
            msg = Message(subject='Redirects Changes',
                          sender='bostonkj.bkj@gmail.com',
                          recipients='bak45247@bethel.edu')
            msg.body = "Nothing to send"
            mail.send(msg)
        return ""

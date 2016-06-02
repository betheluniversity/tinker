__author__ = 'ejc84332'

import re

from tinker import db

from flask import Blueprint, render_template

from flask.ext.classy import FlaskView
from BeautifulSoup import BeautifulSoup

from tinker.new_redirects.redirects_controller import RedirectsController
from tinker.redirects.models import BethelRedirect

RedirectsBlueprint = Blueprint('redirects', __name__, template_folder='templates')

class RedirectsView(FlaskView):
    route_base = '/admin/redirect'

    def __init__(self):
        self.base = RedirectsController()

    def index(self):
        self.base.check_redirect_groups()
        redirects = BethelRedirect.query.all()

        return render_template('redirects.html', **locals())

    def search(self):
        self.base.check_redirect_groups()
        # todo: limit results to...100?
        search_type = self.base.request.form['type']
        search_query = self.base.request.form['search'] + "%"

        if self.base.search == "%" or search_type not in ['from_path', 'to_url']:
            return ""

        if search_type == 'from_path':
            redirects = BethelRedirect.query.filter(BethelRedirect.from_path.like(search_query)).limit(100).all()
        else:
            redirects = BethelRedirect.query.filter(BethelRedirect.to_url.like(search_query)).limit(100).all()
        redirects.sort()
        return render_template('redirect-ajax.html', **locals())

    def new_api_submit(self):
        body = self.base.request.form['body']

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
                # message = "redirect from %s to %s already exists" % (from_url, to_url)
                # sender = 'tinker@bethel.edu'
                # receivers = ['e-jameson@bethel.edu', 'a-vennerstrom@bethel.edu', 'ces55739@bethel.edu']
                #
                # smtp_obj = smtplib.SMTP('localhost')
                # smtp_obj.sendmail(sender, receivers, message)
                # print "Successfully sent email"
                db.session.rollback()
                # return "sent email notice"

        if redirect:
            self.base.create_redirect_text_file()
        return str(redirect)

    def compile_redirects(self):
        self.base.check_redirect_groups()
        resp = self.base.create_redirect_text_file()
        return resp

RedirectsView.register(RedirectsBlueprint)
__author__ = 'ejc84332'

from flask import Blueprint, render_template

from flask.ext.classy import FlaskView
from tinker import db, app
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

    # TODO make comments to the code
    # TODO TEST
    def delete_redirect(self):
        self.base.check_redirect_groups()
        path = self.base.request.form['from_path']

        try:
            redirect = BethelRedirect.query.get(path)
            db.session.delete(redirect)
            db.session.commit()
            resp = self.base.create_redirect_text_file()

        except:
            return "fail"

        return "deleted %s" % resp


    # TODO comment
    # TODO TEST
    def new_redirect_submit(self):
        self.base.check_redirect_groups()
        form = self.base.request.form
        from_path = form['new-redirect-from']
        to_url = form['new-redirect-to']
        short_url = form.get('short-url') == 'on'
        expiration_date = form.get('expiration-date')

        if expiration_date:
            expiration_date = self.base.datetime.datetime.strptime(expiration_date, "%a %b %d %Y")
        else:
            expiration_date = None

        if not from_path.startswith("/"):
            from_path = "/%s" % from_path

        try:
            redirect = BethelRedirect(from_path=from_path, to_url=to_url, short_url=short_url, expiration_date=expiration_date)

            db.session.add(redirect)
            db.session.commit()

            # Update the file after every submit?
            self.base.create_redirect_text_file()
        except:
            # Currently we are unable to track down why multiple redirects are being created. This causes this error:
            # (IntegrityError) column from_path is not unique u'INSERT INTO bethel_redirect (from_path, to_url, short_url, expiration_date)
            # Our work around is to just ignore the issue.
            # hopefully this will catch the error.
            db.session.rollback()
            return ""


        return str(redirect)



    def new_internal_redirect_submit(from_path, to_url, self):
        # added logic to have Tinker be able to internally create a redirect
        self.base.check_redirect_groups()

        if not from_path.startswith("/"):
            from_path = "/%s" % from_path

        # if one from the current from exists, remove it.
        try:
            redirect = BethelRedirect.query.get(from_path)
            db.session.delete(redirect)
            db.session.commit()
            # following variable isn't being used... USED ANYWHERE ELSE?
            # resp = self.base.create_redirect_text_file()
            app.logger.debug(": Correctly deleted if necessary")
        except:
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


    def new_api_submit_asset_expiration(self):
        subject = self.base.request.form['subject']
        soup = self.base.BeautifulSoup(subject)
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

            smtp_obj = self.basesmtplib.SMTP('localhost')
            smtp_obj.sendmail(sender, receivers, message)
            print "Successfully sent email"
            db.session.rollback()
            return "sent email notice"

        if redirect:
            self.base.create_redirect_text_file()

        return str(redirect)

    def delete_expired_redirects(self):
        today = self.base.datetime.datetime.utcnow()
        redirects = BethelRedirect.query.filter(BethelRedirect.expiration_date < today).all()
        for redirect in redirects:
            db.session.delete(redirect)
        db.session.commit()
        self.base.create_redirect_text_file()
        return 'done'

    def test(self):
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

        self.base.create_redirect_text_file()
        resp.append("</pre>")
        return '\n'.join(resp)

RedirectsView.register(RedirectsBlueprint)
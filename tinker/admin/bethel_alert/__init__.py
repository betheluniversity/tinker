# Global
import json
import requests

from flask import render_template, session
from flask_classy import FlaskView, route

# Local
from tinker import app
from tinker.tinker_controller import admin_permissions


class BethelAlertView(FlaskView):
    route_base = '/admin/bethel-alert'

    # This method is called before any request to check user's credentials
    def before_request(self, name, **kwargs):
        admin_permissions(self)

    def index(self):
        return render_template('admin/bethel_alert/home.html', **locals())

    @route("/clear-cache", methods=['post'])
    def clear_cache(self):
        # TODO: still need to clear MyBethel's feed as well!
        try:
            # this route clears the cache
            status_code = requests.get('https://www.bethel.edu/code/news/php/news_article_feed_clear_cache', auth=(app.config['CASCADE_LOGIN']['username'], app.config['CASCADE_LOGIN']['password'])).status_code
            if status_code == 200:
                return json.dumps({
                    'type': 'success',
                    'message': 'Success! The caches have been cleared. You should be able to see your Public Bethel Alert on the applicable feeds.'
                })
            else:
                raise Exception
        except:
            return json.dumps({
                'type': 'danger',
                'message': 'ERROR: Please try again. If it still does not work, contact Web Development.'
            })



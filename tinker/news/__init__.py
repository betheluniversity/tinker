import datetime
from createsend import *

# tinker
from tinker import app
from tinker.tinker_controller import requires_auth

# news controller
from campaign_controller import NewsController

# flask
from flask import Blueprint, render_template, url_for, redirect, session
from flask_classy import FlaskView, route, request

NewsBlueprint = Blueprint('news', __name__, template_folder='templates')


class NewsView(FlaskView):
    route_base = '/news'

    def __init__(self):
        self.base_campaign = NewsController()

    def before_request(self, name, **kwargs):
        pass

    def index(self):
        return 'test'

    @route("/public/create_and_send_campaign", methods=['get', 'post'])
    @route("/public/create_campaign", methods=['get', 'post'])
    @route("/public/create_campaign/<date>", methods=['get', 'post'])
    # @requires_auth
    def create_campaign(self, date=None):
        resp = None
        if not date:
            date = datetime.datetime.strptime(datetime.datetime.now().strftime("%m-%d-%Y"), "%m-%d-%Y")
        else:
            date = datetime.datetime.strptime(date, "%m-%d-%Y")

        if 'create_and_send_campaign' in request.url_rule.rule and app.config['ENVIRON'] == 'prod':
            self.base_campaign.log_sentry("News create_and_send_campaign was called on production", date)

        for news_article in self.base_campaign.traverse_xml(app.config['NEWS_XML_URL'], 'system-page', True):
            try:
                news_article_date = news_article['date'].strftime("%m-%d-%Y")
                if news_article_date != date.strftime("%m-%d-%Y"):
                    continue

                # add news_article
                news_article_text = self.base_campaign.create_single_news_article(news_article)
                if news_article_text != '':
                    campaign_monitor_key = app.config['NEWS_CAMPAIGN_MONITOR_KEY']
                    CreateSend({'api_key': campaign_monitor_key})
                    new_campaign = Campaign({'api_key': campaign_monitor_key})

                    client_id = app.config['NEWS_CLIENT_ID']
                    subject = 'Bethel News | ' + news_article['title']
                    name = '%s | %s' % (news_article['title'], str(date.strftime('%m/%-d/%Y')))
                    from_name = 'Bethel News'
                    from_email = 'news@lists.bethel.edu'
                    reply_to = 'news@lists.bethel.edu'
                    list_ids = [app.config['NEWS_LIST_KEY']]
                    segment_ids = [app.config['NEWS_SEGMENT_ID']]
                    template_id = app.config['NEWS_TEMPLATE_ID']
                    template_content = {
                        "Singlelines": [
                            {
                                "Content": news_article_text
                            }
                        ]
                    }

                    # # Todo: someday ---- if a campaign already exists, delete the old one and create a new one
                    resp = new_campaign.create_from_template(client_id, subject, name, from_name, from_email, reply_to,
                                                             list_ids,
                                                             segment_ids, template_id, template_content)
                    #
                    # if 'create_and_send_campaign' in request.url_rule.rule and app.config['ENVIRON'] == 'prod':
                    #     # Send the news out to ALL users at 5:30 am.
                    #     confirmation_email_sent_to = ', '.join(app.config['ADMINS'])
                    #     new_campaign.send(confirmation_email_sent_to, str(date.strftime('%Y-%m-%d')) + ' 05:30')
                    #     self.base_campaign.log_sentry("News campaign was sent", resp)

            except:
                continue

        return 'success'


NewsView.register(NewsBlueprint)
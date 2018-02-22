# Global
import datetime
import HTMLParser

# Packages
from bu_cascade.asset_tools import find
from createsend import Campaign, CreateSend
from flask import Blueprint
from flask_classy import FlaskView, route

# Local
from campaign_controller import NewsController
from tinker import app
from tinker.tinker_controller import requires_auth


class NewsView(FlaskView):
    route_base = '/news'

    def __init__(self):
        self.base_campaign = NewsController()

    def before_request(self, name, **kwargs):
        pass

    @requires_auth
    @route('/api/send-email/<article_id>', methods=['get', 'post'])
    def reset_send_email(self, article_id):
        try:
            parser = HTMLParser.HTMLParser()
            resp = 'failed'
            page = self.base_campaign.read_page(article_id)
            article_asset, md, sd = page.get_asset()

            news_article_datetime = datetime.datetime.fromtimestamp(int(find(sd, 'publish-date', False))/1000)
            current_datetime = datetime.datetime.now()
            send_email_value = find(sd, 'send-email', False)

            if news_article_datetime.strftime("%m-%d-%Y") != current_datetime.strftime("%m-%d-%Y") and send_email_value == 'Yes':
                return "Don't need to send"

            # add news_article
            news_article_text = self.base_campaign.create_single_news_article(article_asset, news_article_datetime)
            news_article_title = parser.unescape(find(md, 'title', False))

            if news_article_text != '':
                campaign_monitor_key = app.config['NEWS_CAMPAIGN_MONITOR_KEY']
                CreateSend({'api_key': campaign_monitor_key})
                new_campaign = Campaign({'api_key': campaign_monitor_key})

                client_id = app.config['NEWS_CLIENT_ID']
                subject = news_article_title + ' | Bethel News'
                name = '%s | %s' % (news_article_title, str(current_datetime.strftime('%m/%-d/%Y')))
                from_name = 'Bethel News'
                from_email = 'news@bethel.edu'
                reply_to = 'news@bethel.edu'
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

                if app.config['ENVIRON'] == 'prod':
                    self.base_campaign.reset_send_email_value(page)

                    resp = new_campaign.create_from_template(client_id, subject, name, from_name, from_email, reply_to,
                                                             list_ids,
                                                             segment_ids, template_id, template_content)

                    now = datetime.datetime.now()
                    now_plus_10 = now + datetime.timedelta(minutes=10)

                    confirmation_email_sent_to = ', '.join(app.config['ADMINS'])
                    new_campaign.send(confirmation_email_sent_to, str(now_plus_10.strftime('%Y-%m-%d %H:%M')))
                    self.base_campaign.log_sentry("News campaign created", resp)

        except:
            return 'failed'

        return resp

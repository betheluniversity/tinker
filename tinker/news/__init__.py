# Global
import datetime
import html
import traceback
import sys
import random

# Packages
from bu_cascade.asset_tools import find
from createsend import Campaign, CreateSend
from flask_classy import FlaskView, request, route
from flask import abort, render_template, session, redirect, url_for

# Local
from tinker.news.campaign_controller import NewsController
from tinker import app
from tinker.tinker_controller import requires_auth


class NewsView(FlaskView):
    route_base = '/news'

    def __init__(self):
        self.base_campaign = NewsController()

    def before_request(self, name, **kwargs):
        pass


    @route('/api/test', methods=['get', 'post'])
    @requires_auth
    def test(self):
       print(request.url_rule.rule)
       return "see console print"

    # Added "create-and-send-email" and "create-email" (mimics the E-annz routes for better debugging)
    @requires_auth
    @route('/api/send-email/<article_id>', methods=['get', 'post'])
    @route('/api/create-email/<article_id>', methods=['get', 'post'])
    @route('/api/create-and-send-email/<article_id>', methods=['get', 'post'])
    @route('/api/create-email-with-preview/<article_id>', methods=['get', 'post'])
    def reset_send_email(self, article_id):
        try:
            resp = 'failed'

            actually_send_email = False
            if 'send-email' in request.url_rule.rule:
                actually_send_email = True

            just_send_preview = False
            if 'with-preview' in request.url_rule.rule:
                just_send_preview = True

            page = self.base_campaign.read_page(article_id)
            article_asset, md, sd = page.get_asset()

            news_article_datetime = datetime.datetime.fromtimestamp(int(find(sd, 'publish-date', False))/1000)
            current_datetime = datetime.datetime.fromtimestamp(int(find(sd, 'publish-date', False))/1000)

            # ignore any that are on a different day, or in _testing
            is_different_day = news_article_datetime.strftime("%m-%d-%Y") != current_datetime.strftime("%m-%d-%Y")
            if is_different_day and actually_send_email:
                return "Cannot send, wrong day"

            is_testing_page = '_testing/' in find(article_asset, 'path', False)
            if is_testing_page and actually_send_email:
                return "Don't need to send, the page is in testing."

            # add news_article
            news_article_text = self.base_campaign.create_single_news_article(article_asset, news_article_datetime)
            news_article_title = html.unescape(find(md, 'title', False))

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
                            "Content": "<p>%s</p>" % news_article_text
                        }
                    ]
                }

                needs_sending = find(sd, 'send-email', False)

                if app.config['ENVIRON'] == 'prod':
                    # Create the campaign and get necessary info for send
                    resp = new_campaign.create_from_template(client_id, subject, name, from_name, from_email, reply_to,
                                                             list_ids, segment_ids, template_id, template_content)
                    now = self.base_campaign.date_without_dst()
                    now_plus_10 = now + datetime.timedelta(minutes=10)
                    confirmation_email_sent_to = ', '.join(app.config['ADMINS'])

                    # if this is a real campaign, send the emails
                    if actually_send_email and needs_sending == "Yes":
                        # Mark this page as having been sent already (bu_cascade)
                        page.update_and_edit('sd', 'send-email', 'No')
                        self.base_campaign.publish(article_id)

                        # Send the emails (createsend)
                        new_campaign.send(confirmation_email_sent_to, str(now_plus_10.strftime('%Y-%m-%d %H:%M')))
                        self.base_campaign.log_sentry("News campaign created", resp)

                    # if this is is not a real campaign, send emails only if a preview is requested
                    else:
                        if just_send_preview:
                            # Mark this page as having been sent already (leave commented when not testing)
                            # page.update_and_edit('sd', 'send-email', 'No')
                            # self.base_campaign.publish(article_id)

                            new_campaign.send_preview(confirmation_email_sent_to)
                            self.base_campaign.log_sentry("News campaign created and sent as preview", resp)
                        else:
                            self.base_campaign.log_sentry("News campaign created but not sent", resp)

            return str(resp)

        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()

            if str(exc_value) == "The CreateSend API responded with the following error - 303: Duplicate Campaign Name":
                self.base_campaign.log_sentry("News had an error. It looks like it tried to send a duplicate campaign, and was stopped, with error", resp)
                return "(CreateSend 303 Error) Duplicate Campaign Name."

            # Only print traceback when testing
            if False:
                print(traceback.format_exc())

            self.base_campaign.log_sentry("News had an error. It seems to have exited without sending the campaign, with error", resp)
            return str(resp)

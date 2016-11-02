import datetime
from createsend import *

# bu-cascade
from bu_cascade.asset_tools import *

# tinker
from tinker import app
from tinker.tinker_controller import requires_auth
from e_announcements_controller import EAnnouncementsController
from campaign_controller import CampaignController

# flask
from flask import Blueprint, render_template, url_for, redirect, session
from flask_classy import FlaskView, route, request

EAnnouncementsBlueprint = Blueprint('e_announcements', __name__, template_folder='templates')


class EAnnouncementsView(FlaskView):
    route_base = '/e-announcements'

    def __init__(self):
        self.base = EAnnouncementsController()
        self.base_campaign = CampaignController()

    def before_request(self, name, **kwargs):
        pass

    def index(self):
        forms = self.base.traverse_xml(app.config['E_ANNOUNCEMENTS_XML_URL'], 'system-block')

        forms.sort(key=lambda item: item['first_date'], reverse=False)
        return render_template('ea-home.html', **locals())

    @route("/delete/<e_announcement_id>", methods=['GET', 'POST'])
    def delete(self, e_announcement_id):
        # must have access to delete
        # if session['groups'] not in 'E-Announcement Approver':
        #     return redirect(url_for('e_announcements.EAnnouncementsView:index'), code=302)

        block = self.base.read_block(e_announcement_id)
        e_announcement_data, mdata, sdata = block.read_asset()

        # todo Check if first date is after today and has gone through workflow
        # if sdata['structuredDataNodes']['structuredDataNode'][3]['text'] == datetime.date.today():
        # print 'Delete E-Announcement ' + e_announcement_id
        self.base.delete(e_announcement_id, 'block')
        self.base.publish(app.config['E_ANNOUNCEMENTS_XML_ID'])

        return render_template('delete-confirm.html', **locals())

    def view(self, e_announcement_id):
        block = self.base.read_block(e_announcement_id)
        asset, mdata, sdata = block.get_asset()

        title = find(mdata, 'title', False)
        message = find(sdata, 'message', False)
        first = find(sdata, 'first-date', False)
        second = find(sdata, 'second-date', False)
        banner_roles = find(mdata, 'banner-roles', False)

        return render_template('view.html', **locals())

    def new(self):
        from forms import EAnnouncementsForm
        form = EAnnouncementsForm()
        new_form = True

        # extra variable the form uses
        brm = self.base.brm
        return render_template('form.html', **locals())

    # @route("/confirm", methods=['GET'])
    @route("/confirm/<status>", methods=['GET'])
    def confirm(self, status='new'):
        return render_template('confirm.html', **locals())

    def edit(self, e_announcement_id):
        from tinker.e_announcements.forms import EAnnouncementsForm

        # if its in the workflow, give a warning
        if self.base.asset_in_workflow(e_announcement_id, asset_type='block'):
            return render_template('in-workflow.html')

        # Get the e-ann data from cascade
        block = self.base.read_block(e_announcement_id)
        e_announcement_data, mdata, sdata = block.read_asset()
        edit_data = self.base.get_edit_data(sdata, mdata)  # (e_announcement_data)

        # readonly values are set if the date is in the past (shouldn't be edited)
        self.base.set_readonly_values(edit_data)
        form = EAnnouncementsForm(**edit_data)

        # extra variable the form uses
        brm = self.base.brm
        if '/duplicate/' in request.url:
            new_form = True

        return render_template('form.html', **locals())

    def duplicate(self, e_announcement_id):
        from tinker.e_announcements.forms import EAnnouncementsForm

        # if its in the workflow, give a warning
        if self.base.asset_in_workflow(e_announcement_id, asset_type='block'):
            return render_template('in-workflow.html')

        # Get the e-ann data from cascade
        block = self.base.read_block(e_announcement_id)
        e_announcement_data, mdata, sdata = block.read_asset()
        edit_data = self.base.get_edit_data(sdata, mdata)  # (e_announcement_data)

        # readonly values are set if the date is in the past (shouldn't be edited)
        self.base.set_readonly_values(edit_data)
        form = EAnnouncementsForm(**edit_data)

        # extra variable the form uses
        brm = self.base.brm
        # TODO: is this if statement necessary in Flask-Classy convention now? It seems to be a given here.
        if '/duplicate/' in request.url:
            new_form = True

        return render_template('form.html', **locals())

    @route("/submit", methods=['post'])
    def submit(self):
        rform = request.form
        eaid = rform.get('e_announcement_id')

        failed = self.base.validate_form(rform)
        if failed:
            return failed

        if not eaid:
            status = "new"
            bid = app.config['E_ANNOUNCEMENTS_BASE_ASSET']
            e_announcement_data, mdata, sdata = self.base.cascade_connector.load_base_asset_by_id(bid, 'block')
            asset = self.base.update_structure(e_announcement_data, sdata, rform, e_announcement_id=eaid)
            resp = self.base.create_block(asset)
            new_eaid = resp.asset['xhtmlDataDefinitionBlock']['id']
            self.base.log_sentry('New e-announcement submission', resp)
        else:
            block = self.base.read_block(eaid)
            e_announcement_data, mdata, sdata = block.read_asset()
            asset = self.base.update_structure(e_announcement_data, sdata, rform, e_announcement_id=eaid)
            resp = str(block.edit_asset(asset))
            self.base.log_sentry("E-Announcement edit submission", resp)

        return render_template('confirm.html', **locals())

    # @route("/create_and_send_campaign", methods=['get', 'post'])
    @route("/create_campaign", methods=['get'])  # , 'post'])
    # @route("/create_campaign/<date>", methods=['get', 'post'])
    @requires_auth
    def create_campaign(self, date=None):
        resp = None
        try:
            if not date:
                date = datetime.datetime.strptime(datetime.datetime.now().strftime("%m-%d-%Y"), "%m-%d-%Y")
            else:
                date = datetime.datetime.strptime(date, "%m-%d-%Y")

            # send a
            if 'create_and_send_campaign' in request.url_rule.rule and app.config['ENVIRON'] == 'prod':
                self.base.log_sentry("E-Announcement create_and_send_campaign was called on production", date)

            if not self.base_campaign.check_if_valid_date(date):
                return 'E-Announcements are not set to run today. No campaign was created and no E-Announcements were sent out.'

            submitted_announcements = []
            current_announcement_role_list = []
            for announcement in self.base.traverse_xml(app.config['E_ANNOUNCEMENTS_XML_URL'], 'system-block'):
                date_matches = False

                if announcement['first_date']:
                    first_date = datetime.datetime.strptime(announcement['first_date'], "%A %B %d, %Y")
                    if str(date) == str(first_date):
                        date_matches = True

                if announcement['second_date']:
                    second_date = datetime.datetime.strptime(announcement['second_date'], "%A %B %d, %Y")
                    if str(date) == str(second_date):
                        date_matches = True

                if not date_matches:
                    continue

                # add announcement
                submitted_announcements.append({
                    "Layout":
                        "announcements",
                    "Multilines": [
                        {
                            "Content": self.base_campaign.create_single_announcement(announcement)
                        }
                    ]
                }
                )

                # create a list of all roles that are currently receiving E-Announcements
                for role in announcement['roles']:
                    if role not in current_announcement_role_list:
                        current_announcement_role_list.append(role)

            campaign_monitor_key = app.config['CAMPAIGN_MONITOR_KEY']
            CreateSend({'api_key': campaign_monitor_key})
            new_campaign = Campaign({'api_key': campaign_monitor_key})

            client_id = app.config['CLIENT_ID']
            subject = 'Bethel E-Announcements | ' + str(date.strftime('%A, %B %-d, %Y'))
            name = 'Bethel E-Announcements | %s | %s' % (str(date.strftime('%A')), str(date.strftime('%m/%-d/%Y')))
            from_name = 'Bethel E-Announcements'
            from_email = 'e-announcements@lists.bethel.edu'
            reply_to = 'e-announcements@lists.bethel.edu'
            list_ids = [app.config['LIST_KEY']]
            segment_ids = [app.config['SEGMENT_ID']]
            template_id = app.config['TEMPLATE_ID']
            template_content = {
                "Singlelines": [
                    {
                        "Content": 'Bethel E-Announcements<br/>' + str(date.strftime('%A, %B %-d, %Y')),
                    },
                    {
                        "Content": '<a href="https://www.bethel.edu/e-announcements/archive?date=%s">View all E-Announcements for today.</a>' % str(
                            date.strftime('%m-%d-%Y'))
                    }
                ],
                "Multilines": [
                    {
                        "Content": self.base_campaign.get_layout_for_no_announcements(current_announcement_role_list),
                    }
                ],
                "Repeaters": [
                    {
                        "Items": submitted_announcements
                    },
                ]
            }

            # Todo: someday ---- if a campaign already exists, delete the old one and create a new one
            resp = new_campaign.create_from_template(client_id, subject, name, from_name, from_email, reply_to,
                                                     list_ids,
                                                     segment_ids, template_id, template_content)

            if 'create_and_send_campaign' in request.url_rule.rule and app.config['ENVIRON'] == 'prod':
                # Send the announcements out to ALL users at 5:30 am.
                confirmation_email_sent_to = ', '.join(app.config['ADMINS'])
                new_campaign.send(confirmation_email_sent_to, str(date.strftime('%Y-%m-%d')) + ' 05:30')
                self.base.log_sentry("E-Announcement campaign was sent", resp)

            return str(resp)

        except:
            self.base.log_sentry("E-Announcements had an error. It seems to have exited without sending the campaign.", resp)
            return str(resp)

    def edit_all(self):
        type_to_find = 'system-block'
        xml_url = app.config['E_ANNOUNCEMENTS_XML_URL']
        self.base.edit_all(type_to_find, xml_url)
        return 'success'

EAnnouncementsView.register(EAnnouncementsBlueprint)

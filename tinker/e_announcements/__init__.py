# Global
import datetime
import json

from bu_cascade.asset_tools import find
from createsend import Campaign, CreateSend
from flask import abort, render_template, session
from flask_classy import FlaskView, request, route
from collections import OrderedDict

# Local
from tinker import app, cache
from tinker.tinker_controller import requires_auth
from tinker.e_announcements.e_announcements_controller import EAnnouncementsController
from tinker.e_announcements.campaign_controller import CampaignController


class EAnnouncementsView(FlaskView):
    route_base = '/e-announcements'

    def __init__(self):
        self.base = EAnnouncementsController()
        self.base_campaign = CampaignController()

    def before_request(self, name, **kwargs):
        pass

    def index(self):
        username = session['username']

        # Username is needed for caching purposes
        @cache.memoize(timeout=300)
        def index_cache(username):
            forms = self.base.traverse_xml(app.config['E_ANNOUNCEMENTS_XML_URL'], 'system-block')

            forms.sort(key=lambda item: datetime.datetime.strptime(item['first_date'], '%A %B %d, %Y'), reverse=True)

            if 'E-Announcement Approver' in session['groups']:
                # The special admin view
                all_schools = OrderedDict({
                    1: 'My E-Announcements',
                    2: 'All E-Announcements',
                    3: 'Other E-Announcements'},
                    key=lambda t: t[0]
                )
            else:
                all_schools = OrderedDict({
                    1: 'User E-Announcements'}
                )
            return render_template('e-announcements/home.html', **locals())
        return index_cache(username)

    @route("/delete/<e_announcement_id>", methods=['GET', 'POST'])
    def delete(self, e_announcement_id):
        # must have access to delete
        # if session['groups'] not in 'E-Announcement Approver':
        #     return redirect(url_for('EAnnouncementsView:index'), code=302)

        block = self.base.read_block(e_announcement_id)
        e_announcement_data, mdata, sdata = block.read_asset()

        # todo Check if first date is after today and has gone through workflow
        # if sdata['structuredDataNodes']['structuredDataNode'][3]['text'] == datetime.date.today():
        # print 'Delete E-Announcement ' + e_announcement_id
        self.base.delete(e_announcement_id, 'block')
        self.base.publish(app.config['E_ANNOUNCEMENTS_XML_ID'])

        return render_template('e-announcements/delete-confirm.html', **locals())

    def view(self, e_announcement_id):
        block = self.base.read_block(e_announcement_id)
        asset, mdata, sdata = block.get_asset()

        title = find(mdata, 'title', False)
        message = find(sdata, 'message', False)
        first = find(sdata, 'first-date', False)
        second = find(sdata, 'second-date', False)
        banner_roles = find(mdata, 'banner-roles', False)

        return render_template('e-announcements/view.html', **locals())

    # CANT CACHE THIS
    def new(self):
        from tinker.e_announcements.forms import EAnnouncementsForm
        form = EAnnouncementsForm()
        new_form = True

        # extra variable the form uses
        brm = self.base.brm
        return render_template('e-announcements/form.html', **locals())

    # @route("/confirm", methods=['GET'])
    @route("/confirm/<status>", methods=['GET'])
    def confirm(self, status='new'):
        return render_template('e-announcements/confirm.html', **locals())

    def edit(self, e_announcement_id):
        from tinker.e_announcements.forms import EAnnouncementsForm

        # if its in the workflow, give a warning
        if self.base.asset_in_workflow(e_announcement_id, asset_type='block'):
            return render_template('e-announcements/in-workflow.html')

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

        return render_template('e-announcements/form.html', **locals())

    def duplicate(self, e_announcement_id):
        from tinker.e_announcements.forms import EAnnouncementsForm

        # if its in the workflow, give a warning
        if self.base.asset_in_workflow(e_announcement_id, asset_type='block'):
            return render_template('e-announcements/in-workflow.html')

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

        return render_template('e-announcements/form.html', **locals())

    @route("/submit", methods=['post'])
    def submit(self):
        rform = request.form
        app.logger.debug("E-Announcement Submit: {0} - {1}: {2}".format(session['username'], datetime.datetime.now(), rform))
        eaid = rform.get('e_announcement_id')

        form, passed = self.base.validate_form(rform)
        if not passed:
            if 'e_announcement_id' in rform.keys():
                e_announcement_id = rform['e_announcement_id']
            else:
                new_form = True
            # bring in the mapping
            brm = self.base.brm
            return render_template('e-announcements/form.html', **locals())

        if not eaid:
            status = "new"
            bid = app.config['E_ANNOUNCEMENTS_BASE_ASSET']
            e_announcement_data, mdata, sdata = self.base.cascade_connector.load_base_asset_by_id(bid, 'block')
            asset = self.base.update_structure(e_announcement_data, rform, e_announcement_id=eaid)
            resp = self.base.create_block(asset)
            new_eaid = resp.asset['xhtmlDataDefinitionBlock']['id']
            self.base.log_sentry('New e-announcement submission', resp)
        else:
            block = self.base.read_block(eaid)
            e_announcement_data, mdata, sdata = block.read_asset()
            asset = self.base.update_structure(e_announcement_data, rform, e_announcement_id=eaid)
            # TODO: maybe add cascade logger here? would like it in block.edit_asset, but that's in bu_cascade
            resp = str(block.edit_asset(asset))
            self.base.log_sentry("E-Announcement edit submission", resp)

        return render_template('e-announcements/confirm.html', **locals())

    @route("/public/create_and_send_campaign", methods=['get', 'post'])
    @route("/public/create_campaign", methods=['get', 'post'])
    @route("/public/create_campaign/<date>", methods=['get', 'post'])
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
            for announcement in self.base.traverse_xml(app.config['E_ANNOUNCEMENTS_XML_URL'], 'system-block', True):
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
                announcement_text = self.base_campaign.create_single_announcement(announcement)
                if announcement_text != '':
                    submitted_announcements.append({
                        "Layout":
                            "announcements",
                        "Multilines": [
                            {
                                "Content": announcement_text
                            }
                        ]
                    })

                # create a list of all roles that are currently receiving E-Announcements
                for role in announcement['roles']:
                    if role not in current_announcement_role_list:
                        current_announcement_role_list.append(role)

            campaign_monitor_key = app.config['E_ANNOUNCEMENTS_CAMPAIGN_MONITOR_KEY']
            CreateSend({'api_key': campaign_monitor_key})
            new_campaign = Campaign({'api_key': campaign_monitor_key})

            client_id = app.config['E_ANNOUNCEMENTS_CLIENT_ID']
            subject = 'Bethel E-Announcements | ' + str(date.strftime('%A, %B %-d, %Y'))
            name = 'Bethel E-Announcements | %s | %s' % (str(date.strftime('%A')), str(date.strftime('%m/%-d/%Y')))
            from_name = 'Bethel E-Announcements'
            from_email = 'e-announcements@lists.bethel.edu'
            reply_to = 'e-announcements@lists.bethel.edu'
            list_ids = [app.config['E_ANNOUNCEMENTS_LIST_KEY']]
            segment_ids = [app.config['E_ANNOUNCEMENTS_SEGMENT_ID']]
            template_id = app.config['E_ANNOUNCEMENTS_TEMPLATE_ID']
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
            self.base.cascade_call_logger(locals())
            self.base.log_sentry("E-Announcement campaign was created", resp)

            if 'create_and_send_campaign' in request.url_rule.rule and app.config['ENVIRON'] == 'prod':
                # Send the announcements out to ALL users at 5:30 am.
                confirmation_email_sent_to = ', '.join(app.config['ADMINS'])
                new_campaign.send(confirmation_email_sent_to, str(date.strftime('%Y-%m-%d')) + ' 5:30')
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

    @route("/upcoming")
    def ea_upcoming(self):
        if 'E-Announcement Approver' not in session['groups'].split(';') and 'Administrators' not in session['groups'].split(';'):
            return abort(403)

        return render_template("e-announcements/future.html")

    @route("/ea_future", methods=['POST'])
    def ea_future(self):
        if 'E-Announcement Approver' not in session['groups'].split(';') and 'Administrators' not in session['groups'].split(';'):
            return abort(403)

        pass_in = request.form
        date_id = pass_in.get('dateId', 'null')
        ea_display = []

        forms = self.base.traverse_xml(app.config['E_ANNOUNCEMENTS_XML_URL'], 'system-block', True)
        forms.sort(key=lambda item: ['created_on'], reverse=True)

        self.base.get_upcoming(forms, date_id, ea_display)

        return render_template("e-announcements/future-ajax.html", **locals())

    # TODO e-announcements by role (someday)

    @route("/search", methods=['POST'])
    def search(self):
        data = json.loads(request.data)
        selection = data['selection']
        title = data['title']
        date = data['date']
        try:
            date = datetime.datetime.strptime(date, "%a %b %d %Y")
        except:
            date = 0

        search_results, forms_header = self.base.get_search_results(selection, title, date)
        search_results.sort(key=lambda item: datetime.datetime.strptime(item['first_date'], '%A %B %d, %Y'), reverse=True)

        today = datetime.datetime.today()
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)

        def get_day_before(dto):
            yester = dto - datetime.timedelta(days=1)

            return yester

        count = 0
        for result in search_results:
            if result['first_date_past']:
                search_results[count]['editable'] = False
            else:
                search_results[count]['editable'] = True

                first_date = datetime.datetime.strptime(result['first_date'].replace(',', ''), '%A %B %d %Y')
                day_before = get_day_before(first_date)

                while self.base.is_bethel_holiday(day_before) or day_before.weekday() > 4:  # while the day before is a holiday
                    if today.month == day_before.month and today.day == day_before.day \
                            and today.year == day_before.year:  # if today is the same day as a holiday or weekend make un-editable
                        search_results[count]['editable'] = False
                        break
                    day_before = get_day_before(day_before)  # go one day backwards
                # If the today isn't a holiday or weekend, and it is after 1pm, make e-annz uneditable
                if today.month == day_before.month and today.day == day_before.day and today.year == day_before.year \
                        and today.hour >= 13:
                    search_results[count]['editable'] = False

            count += 1

        return render_template('e-announcements/results.html', **locals())

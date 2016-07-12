import datetime
from createsend import *
from flask import render_template
from tinker.tinker_controller import TinkerController


class CampaignController(TinkerController):
    # creates the campaign monitor 'if' structure along with the html
    def create_single_announcement(self, announcement):
        return_value = ''
        count = 1

        for role in announcement['roles']:
            prepended_role = '20322-%s' % role
            if count == 1:
                return_value = '[if:%s=Y]' % prepended_role
            else:
                return_value += '[elseif:%s=Y]' % prepended_role

            return_value += self.e_announcement_html(announcement)
            count = count + 1

        return_value += '[endif]'

        return return_value

    # builds the html
    def e_announcement_html(self, announcement):
        title = announcement['title']
        message = announcement['message']
        return render_template('announcement.html', **locals())

    # Checks if the date provided is a valid date
    # Valid days are 1) not in the past
    #                2) is a M/W/F
    #                3) not between 12/24 - 1/1
    def check_if_valid_date(self, date):
        # check if the date is after yesterday at midnight
        if date < datetime.datetime.combine(date.today(), datetime.time.min):
            return False

        # Check if day is mon/wed/fri
        if date.weekday() in [1, 3, 5, 6]:
            return False

        # Check if date is between 12/24 and 1/1
        dates_to_ignore = ['12/24', '12/25', '12/26', '12/27', '12/28', '12/29', '12/30', '12/31', '1/1']
        current_month_day = str(date.month) + '/' + str(date.day)
        if current_month_day in dates_to_ignore:
            return False

        return True

    def get_layout_for_no_announcements(self, roles):
        if_block = ''
        count = 1

        # We are looping through the roles that are receiving at least one e-announcement.
        # If no roles match, then give some default text
        for role in roles:
            prepended_role = '20322-%s' % role
            if count == 1:
                if_block += '[if:%s=Y]' % prepended_role
            else:
                if_block += '[elseif:%s=Y]' % prepended_role

            count += 1

        return if_block + '[else]%s[endif]' % '<p>There are no E-Announcements for you today.</p>'

    # Not currently used. However, this is helpful to find template IDs
    def get_templates_for_client(self, campaign_monitor_key, client_id):
        for template in Client({'api_key': campaign_monitor_key}, client_id).templates():
            print template.TemplateID


    # Not currently used. However, this is helpful to find segment IDs
    def get_segments_for_client(self, campaign_monitor_key, client_id):
        for segment in Client({'api_key': campaign_monitor_key}, client_id).segments():
            print segment.SegmentID

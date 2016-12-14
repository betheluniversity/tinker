import datetime
from dateutil.easter import *

import math
from createsend import *

# flask
from flask import render_template

# tinker
from tinker.tinker_controller import TinkerController


class CampaignController(TinkerController):
    # creates the campaign monitor 'if' structure along with the html
    def create_single_announcement(self, announcement):
        return_value = ''
        count = 1

        if len(announcement['roles']) > 0:
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
        holidays = self.is_bethel_holiday(date)
        current_month_day = str(date.month) + '/' + str(date.day)
        if current_month_day in dates_to_ignore:
            return False

        return True

    def is_bethel_holiday(self, date):
        # new years
        if date.month == 1 and date.day == 1:
            return True
        # bonus new years day
        elif date.month == 1 and date.weekday == 1 and date.day == 2:
            return True
        # MLK - 3rd monday in jan
        elif date.month == 1 and date.weekday == 1 and math.ceil(date.day/7) == 3:
            return True
        # Easter
        elif self.is_friday_before_easter(date):
            return True
        # memorial day - last monday in may (may, date is after 24th and its a monday)
        elif date.month == 5 and date.weekday == 1 and date.day >= 24:
            return True
        # july 4
        elif date.month == 7 and date.day == 4:
            return True
        # labor day - first monday in sept
        elif date.month == 9 and date.weekday == 1 and math.ceil(date.day/7) == 1:
            return True
        # Thanksgiving and Black Friday - 4th thursday/friday in november
        elif date.month == 11 and math.ceil(date.day/7) == 4 and (date.weekday == 4 or date.weekday == 5):
            return True
        # bonus Christmas eve day -- if christmas eve is on a Saturday, we get the Friday off
        elif date.month == 12 and date.weekday == 5 and date.day == 23:
            return True
        # christmas on
        elif date.month == 12 and date.day >= 24:
            return True

        return False

    def is_friday_before_easter(self, date):
        easter_day = easter(date.year)

        if date.month == easter_day.month and easter_day.weekday - 2 == date.day:
            return True

        return False

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

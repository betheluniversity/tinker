import datetime
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
    #                3) not a holiday
    def check_if_valid_date(self, date):
        # check if the date is after yesterday at midnight
        if date < datetime.datetime.combine(date.today(), datetime.time.min):
            return False

        # Check if day is mon/wed/fri
        if date.weekday() in [1, 3, 5, 6]:
            return False

        if self.is_bethel_holiday(date):
            return False

        return True

    def is_bethel_holiday(self, date):
        # New years
        if date.month == 1 and date.day == 1:
            return True
        # New Years(observed) -- If new years day is on the weekend, we get the monday off (2nd or 3rd)
        elif date.month == 1 and date.weekday() == 0 and (date.day == 2 or date.day == 3):
            return True
        # MLK Day - 3rd monday in jan
        elif date.month == 1 and date.weekday() == 0 and math.ceil(date.day/7.0) == 3:
            return True
        # Easter (is the date the friday before easter)
        elif self.is_date_friday_before_easter(date):
            return True
        # memorial day - last monday in may (may, date is after 24th and its a monday)
        elif date.month == 5 and date.day > 24 and date.weekday() == 0:
            return True
        # july 4
        elif date.month == 7 and date.day == 4:
            return True
        # Labor Day - first monday in sept
        elif date.month == 9 and date.weekday() == 0 and math.ceil(date.day/7.0) == 1:
            return True
        # Black Friday -- 4th friday in nov
        elif date.month == 11 and math.ceil(date.day/7.0) == 4 and date.weekday() == 4:
            return True
        # Christmas Eve(observed) - christmas eve is on the weekend, we get the friday off (22nd or 23rd).
        elif date.month == 12 and date.weekday() == 4 and (date.day == 22 or date.day == 23):
            return True
        # christmas days
        elif date.month == 12 and date.day >= 24:
            return True

        return False

    def is_date_friday_before_easter(self, date):
        year = date.year

        # code from http://code.activestate.com/recipes/576517-calculate-easter-western-given-a-year/
        a = year % 19
        b = year // 100
        c = year % 100
        d = (19 * a + b - b // 4 - ((b - (b + 8) // 25 + 1) // 3) + 15) % 30
        e = (32 + 2 * (b % 4) + 2 * (c // 4) - d - (c % 4)) % 7
        f = d + e - 7 * ((a + 11 * d + 22 * e) // 451) + 114
        month = f // 31
        day = f % 31 + 1

        return date.month == month and date.day == (day - 2)

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

        # If no e-annz exist for the day, make sure that a proper message is displayed.
        if if_block == '':
            if_block = '<p>There are no E-Announcements for you today.</p>'
        else:
            if_block += '[else]%s[endif]' % '<p>There are no E-Announcements for you today.</p>'

        return if_block


# Global
import datetime

# Packages
from flask import render_template

# Local
from tinker.tinker_controller import TinkerController
from tinker.e_announcements.e_announcements_controller import EAnnouncementsController


class CampaignController(TinkerController):

    def __init__(self):
        super(CampaignController, self).__init__()
        self.base = EAnnouncementsController()

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
        return render_template('e-announcements/announcement.html', **locals())

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

        if self.base.is_bethel_holiday(date):
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

        # If no e-annz exist for the day, make sure that a proper message is displayed.
        if if_block == '':
            if_block = '<p>There are no E-Announcements for you today.</p>'
        else:
            if_block += '[else]%s[endif]' % '<p>There are no E-Announcements for you today.</p>'

        return if_block

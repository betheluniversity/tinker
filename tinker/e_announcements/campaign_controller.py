import datetime

from flask import session
from flask import render_template
from tinker import app
from tinker.tinker_controller import TinkerController


class CampaignController(TinkerController):
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

    def e_announcement_html(self, announcement):
        element = '''
            <table class="layout layout--no-gutter" style="border-collapse: collapse;table-layout: fixed;Margin-left: auto;Margin-right: auto;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: #ffffff;" align="center">
                <tbody>
                    <tr>
                        <td class="column" style="padding: 0;text-align: left;vertical-align: top;color: #555;font-size: 14px;line-height: 21px;font-family: Georgia,serif;width: 600px;">
                            <div style="Margin-left: 20px;Margin-right: 20px;">
                                <h2 style="Margin-top: 0;Margin-bottom: 16px;font-style: normal;font-weight: normal;color: #555;font-size: 20px;line-height: 28px;font-family: sans-serif;">
                                    <strong>%s</strong>
                                </h2>
                            </div>
                            <div style="Margin-left: 20px;Margin-right: 20px;">
                                %s
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
            <div style="font-size: 50px;line-height: 60px;mso-line-height-rule: exactly;">&nbsp;</div>
        ''' % (announcement['title'], announcement['message'])

        return element

    # Gets the template IDs
    def get_templates_for_client(self, campaign_monitor_key, client_id):
        for template in Client({'api_key': campaign_monitor_key}, client_id).templates():
            print template.TemplateID

    # Gets the template IDs
    def get_segments_for_client(self, campaign_monitor_key, client_id):
        for segment in Client({'api_key': campaign_monitor_key}, client_id).segments():
            print segment.SegmentID

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

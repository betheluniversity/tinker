# Global
import datetime
import re

# Packages
from bu_cascade.asset_tools import find, update
from flask import session

# Local
from tinker import app
from tinker.tinker_controller import TinkerController


class OfficeHoursController(TinkerController):

    def __init__(self):
        super(OfficeHoursController, self).__init__()
        self.datetime_format = "%I:%M %p"

    def inspect_child(self, child, find_all=False):
        username = session['username']
        try:
            if 'Administrators' in session['groups'] or self.can_user_access_block(child.attrib['id']):
                return self._iterate_child_xml(child, username)
            else:
                return None
        except:
            return None

    def _iterate_child_xml(self, child, author):

        page_values = {
            'author': author,
            'id': child.attrib['id'] or "",
            'title': child.find('title').text or None,
            'created-on': child.find('created-on').text or None,
        }

        return page_values

    def separate_office_hours(self, forms):
        standard_hours = None
        office_hours = []
        for form in forms:
            if form['id'] == app.config['OFFICE_HOURS_STANDARD_BLOCK']:
                standard_hours = form
            else:
                office_hours.append(form)

        return standard_hours, office_hours

    def load_office_hours_block(self, block_id=app.config['OFFICE_HOURS_STANDARD_BLOCK']):
        multiple = ['exceptions']

        block = self.read_block(block_id)

        data, mdata, sdata = block.read_asset()
        edit_data = self.get_edit_data(sdata, mdata,  multiple=multiple)

        return edit_data, sdata, mdata

    def get_exceptions(self, form):
        exceptions = []
        for i in range(1, 200):
            i = str(i)
            try:
                date = 'date' + i
                open = 'open' + i
                close = 'close' + i

                try:
                    date = form[date]
                    open = self.date_to_java_unix(form[open])
                    close = self.date_to_java_unix(form[close])

                except:
                    continue

                date = datetime.datetime.strptime(date, '%m/%d/%Y')
                date = date.strftime('%m-%d-%Y')

                exceptions.append({'date': date, 'open': open, 'close': close})

            except KeyError:
                break

        return exceptions

    def update_structure(self, data, mdata, rform):
        wysiwyg_keys = ['']

        add_data = self.get_add_data(mdata, rform, wysiwyg_keys)
        add_data['exceptions'] = self.get_exceptions(rform)
        for key, value in add_data.iteritems():
            if not value:
                continue

            # any open/close times
            if 'open' in key or 'close' in key and key not in ['next_closed_for_chapel']:
                add_data[key] = self.date_to_java_unix(value)

            if 'date' in key:
                # form is returning default format even though it was overridden.
                # so, translate to date and then back into Cascade format.
                date = datetime.datetime.strptime(value, '%m/%d/%Y')
                add_data[key] = date.strftime('%m-%d-%Y')

        self.update_asset(data, add_data)
        self.rotate_hours(data)

        return data

    # todo: convert this method to use a render_template method
    def convert_week_dict_to_string(self, week_dict):
        summary_html = ''
        has_chapel = False

        summary_html += '<table>'
        for day in week_dict:
            add_chapel = ''
            if day.get('chapel'):
                has_chapel = True
                add_chapel = '*'

            summary_html += '<tr>'
            summary_html += '<td>%s%s</td><td>%s</td>' % (day.get('day'), add_chapel, day.get('time'))
            summary_html += '</tr>'

        summary_html += '</table>'

        if has_chapel:
            summary_html += '<p>*Closed 10:10-11a.m. for chapel.</p>'
        return summary_html

    def convert_ampm(self, date):
        # add in extra spaces, in addition to changing the text
        return date.replace('AM', ' a.m.').replace('PM', ' p.m.')

    def convert_to_noon_or_midnight(self, datestring):
        if '12:00' in datestring:
            if 'AM' in datestring:
                return 'midnight'
            else:
                return 'noon'
        return datestring

    def convert_timestamps_to_bethel_string_hours_only(self, open, close):
        try:
            open = datetime.datetime.fromtimestamp(int(open) / 1000).strftime('%-I:%M%p')
            close = datetime.datetime.fromtimestamp(int(close) / 1000).strftime('%-I:%M%p')

            # if times are 12:00 -- adjust to noon or midnight
            open = self.convert_to_noon_or_midnight(open)
            close = self.convert_to_noon_or_midnight(close)

            # if :00 -- remove it
            open = open.replace(':00', '')
            close = close.replace(':00', '')

            # if times are both am/pm -- remove am/pm on first
            if ('AM' in open and 'AM' in close) or ('PM' in open and 'PM' in close):
                open = open.replace('AM', '').replace('PM', '')

            # convert AM to a.m. and PM to p.m
            open = self.convert_ampm(open)
            close = self.convert_ampm(close)

            return open + ' - ' + close
        except:
            return 'Closed'

    def rotate_hours(self, sdata):
        next_start_date = find(sdata, 'next_start_date', False)

        # if there are next_hours, shift!
        if next_start_date is not None and next_start_date != '':
            # set the current hours if the next_start_date is before today
            if datetime.datetime.now() >= datetime.datetime.strptime(next_start_date, '%m-%d-%Y'):
                week_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

                for week_day in week_days:
                    try:
                        # gather keys
                        open_key = week_day + '_open'
                        next_open_key = 'next_' + week_day + '_open'
                        close_key = week_day + '_close'
                        next_close_key = 'next_' + week_day + '_close'

                        # find values
                        next_open = find(sdata, next_open_key, False)
                        next_close = find(sdata, next_close_key, False)

                        # update values
                        update(sdata, open_key, next_open)
                        update(sdata, close_key, next_close)

                    except:
                        continue

                update(sdata, 'closed_for_chapel', find(sdata, 'next_closed_for_chapel', False))

        # build summary/chapel and exceptions
        initial_summary = '<h3>Office Hours</h3>' + self.create_summary(sdata, 'next_') + self.create_exceptions_text(sdata)
        update(sdata, 'summary', initial_summary)

        # build summary for next (if it applies)
        if self.is_date_within_two_weeks(next_start_date):
            next_summary = self.create_summary(sdata, 'next_')
            next_title = '<h4>New hours starting %s </h4>' % (datetime.datetime.strptime(next_start_date, '%m-%d-%Y').strftime('%A, %B %d, %Y'))

            new_summary = initial_summary + next_title + next_summary

            update(sdata, 'summary', new_summary)

        # finally, put divs around everything
        final_summary = "<div>%s</div>" % find(sdata, "summary", False)
        update(sdata, 'summary', final_summary)

    def create_summary(self, data, dict_prefix=''):
        week_dict = []
        week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        for week_day in week_days:
            week_day_lower = week_day.lower()
            try:
                open_key = dict_prefix + week_day_lower + '_open'
                close_key = dict_prefix + week_day_lower + '_close'

                open = find(data, open_key, False)
                close = find(data, close_key, False)
                chapel = find(data, dict_prefix + 'closed_for_chapel', False)

                if week_day in ['Monday', 'Wednesday', 'Friday'] and chapel == 'Yes':
                    chapel = True
                else:
                    chapel = False

                week_dict.append({
                    'day': week_day,
                    'time': self.convert_timestamps_to_bethel_string_hours_only(open, close),
                    'chapel': chapel,
                })
            except:  # if a open/close key doesn't exist, set 'Closed'
                week_dict.append({
                    'day': week_day,
                    'time': 'Closed',
                    'chapel': False,
                })

        summary = self.convert_week_dict_to_string(week_dict)

        return summary

    def create_exceptions_text(self, sdata):
        dates_seen = []

        # defined as a method since vacation exception and normal office exceptions use the same process
        def loop_over_exceptions(sdata):
            exceptions_text = []
            exceptions_to_keep = []
            exceptions_list = find(sdata, 'exceptions')

            # a default check to make sure the exceptions_list is not a dict
            if type(exceptions_list) is dict:
                exceptions_list = [exceptions_list]

            for exception in exceptions_list:
                date = find(exception, 'date', False)
                if self.is_date_within_two_weeks(date):
                    # make sure that only one exception is added each day, with preference to vacation
                    if date not in dates_seen:
                        dates_seen.append(date)

                        open = find(exception, 'open', False)
                        close = find(exception, 'close', False)

                        date_timestamp = datetime.datetime.strptime(date, '%m-%d-%Y')

                        exceptions_text.append({
                            'html': '<p>%s: %s</p>' % (date_timestamp.strftime('%A, %B %d, %Y'), self.convert_timestamps_to_bethel_string_hours_only(open, close)),
                            'sort-date': date_timestamp
                        })
                if self.is_date_after_today(date):
                    exceptions_to_keep.append(exception)

            # keep exceptions that are today or after
            self.update_asset(sdata, {'exceptions': exceptions_to_keep})

            return exceptions_text

        # pull in vacation hours from General BU Office Hours
        bu_standard_hours = self.read(app.config['OFFICE_HOURS_STANDARD_BLOCK'], 'block')
        vacation_exception_array = loop_over_exceptions(bu_standard_hours)

        # create office exceptions
        # if the current block is the OFFICE_HOURS_STANDARD_BLOCK, it will loop over itself twice, but do nothing.
        # I think its better to simply ignore the check, in order to loop twice.
        office_exception_array = loop_over_exceptions(sdata)

        # merge and sort the vacation hours
        all_exceptions = sorted(vacation_exception_array + office_exception_array, key=lambda x: x['sort-date'])

        # todo: add in exceptions header
        return ''.join(exception['html'] for exception in all_exceptions)

    def is_date_within_two_weeks(self, date):
        if date:
            timedelta_in_days = (datetime.datetime.strptime(date, '%m-%d-%Y').date() - datetime.datetime.now().date()).days
            if 0 <= timedelta_in_days and timedelta_in_days <= 14:  # within 2 weeks
                return True
        return False

    def is_date_after_today(self, date):
        if date:
            timedelta_in_days = (datetime.datetime.strptime(date, '%m-%d-%Y').date() - datetime.datetime.now().date()).days
            if timedelta_in_days >= 0:
                return True
        return False

    def can_user_access_block(self, block_id):
        identifier = {
            'id': block_id,
            'type': 'block',
        }

        # todo: maybe move this to bu_cascade
        my_array = self.cascade_connector.client.service.readAccessRights(self.cascade_connector.login,identifier).accessRightsInformation.aclEntries.aclEntry

        for item in my_array:
            if item.type == 'group' and item.name in session['groups']:
                return True
        return False

    # todo: leave this code please, I want this test in version control for the time being.
    # def is_current_user_in_iam_group(self, group):
    #     user_in_group = False
    #     try:
    #         con = ldap.initialize('ldap://bsp-ldap.bu.ac.bethel.edu:389')
    #         con.simple_bind_s('BU\svc-tinker', app.config['LDAP_SVC_TINKER_PASSWORD'])
    #         results = con.search_s('ou=Bethel Users,dc=bu,dc=ac,dc=bethel,dc=edu', ldap.SCOPE_SUBTREE,
    #                                "(cn=" + session['username'] + ")")
    #         # code to get all users in a group
    #         # con.search_s('ou=Bethel Users,dc=bu,dc=ac,dc=bethel,dc=edu', ldap.SCOPE_SUBTREE, "(|(&(objectClass=Person)(memberof=cn=webadmin,OU=Groups,DC=bu,DC=ac,DC=bethel,DC=edu)))")
    #
    #         for result in results[0][1].get('memberOf'):
    #             if group in result:
    #                 user_in_group = True
    #     except:
    #         pass
    #
    #     return user_in_group

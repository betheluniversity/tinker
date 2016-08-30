import datetime
import re

from flask import session
from flask import render_template
from tinker import app
from bu_cascade.asset_tools import *

from tinker.tinker_controller import TinkerController


class OfficeHoursController(TinkerController):

    def __init__(self):
        super(OfficeHoursController, self).__init__()
        self.datetime_format = "%I:%M %p"

    def _iterate_child_xml(self, child, author):

        page_values = {
            'author': author,
            'id': child.attrib['id'] or "",
            'title': child.find('title').text or None,
            'created-on': child.find('created-on').text or None,
        }

        return page_values

    def inspect_child(self, child):
        # todo add permissions logic
        author = session['username']
        return self._iterate_child_xml(child, author)

    def load_office_hours_block(self, block_id=app.config['OFFICE_HOURS_STANDARD_BLOCK']):
        multiple = ['exceptions']

        block = self.read_block(block_id)

        data, mdata, sdata = block.read_asset()

        #####################################################
        # def pretty_print(object, level=0):
        #     indent = "    "
        #     if isinstance(object, list):
        #         print level * indent + "["
        #         for item in object:
        #             pretty_print(item, level+1)
        #         print level * indent + "]"
        #     elif isinstance(object, dict):
        #         print level * indent + "{"
        #         for key in object:
        #             print (level + 1) * indent + key + ":"
        #             pretty_print(object[key], level + 2)
        #         print level * indent + "}"
        #     else:
        #         print level * indent + str(object)
        # print "mdata:"
        # pretty_print(mdata)
        #####################################################

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

            if 'open' in key or 'close' in key and key not in ['next_closed_for_chapel']:
                add_data[key] = self.date_to_java_unix(value)

            if 'date' in key:
                # form is returning default format even though it was overridden.
                # so, translate to date and then back into Cascade format.
                date = datetime.datetime.strptime(value, '%m/%d/%Y')
                add_data[key] = date.strftime('%m-%d-%Y')

        self.update_asset(data, add_data)

        return data

    def create_summary(self, data, prefix='', show_chapel_text=True):
        week_dict = []
        week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        for week_day in week_days:
            week_day_lower = week_day.lower()
            try:
                open_key = prefix + week_day_lower + '_open'
                close_key = prefix + week_day_lower + '_close'

                open = find(data, open_key, False)
                close = find(data, close_key, False)
                chapel = find(data, prefix + 'closed_for_chapel', False)

                if week_day in ['Monday', 'Wednesday', 'Friday'] and chapel == 'Yes':
                    chapel = 'Yes'
                else:
                    chapel = 'No'

                week_dict.append({
                    'day': week_day,
                    'time': self.convert_timestamps_to_bethel_string(open, close),
                    'chapel': chapel,
                })
            except:  # if a open/close key doesn't exist, set 'Closed'
                week_dict.append({
                    'day': week_day,
                    'time': 'Closed',
                    'chapel': 'No',
                })
                continue

        summary = self.convert_week_dict_to_string(week_dict, show_chapel_text)

        return summary

    def convert_week_dict_to_string(self, week_dict, show_chapel_text=True):
        summary = []
        has_chapel = False

        for day in week_dict:
            chapel = day.get('chapel')
            if chapel == 'Yes':
                add_chapel = '*'
                has_chapel = True
            else:
                add_chapel = ''
            summary.append(day.get('day') + add_chapel + ': ' + day.get('time'))

        summary = '</br>'.join(summary)
        if has_chapel and show_chapel_text:
            summary += '<p>*Closed 10:10-11a.m. for chapel.</p>'
        return summary

    def convert_ampm(self, date):
        return date.replace('AM', 'a.m.').replace('PM', 'p.m.')

    def convert_to_noon_or_midnight(self, datestring):
        if '12:00' in datestring:
            if 'AM' in datestring:
                return 'midnight'
            else:
                return 'noon'
        return datestring

    def convert_timestamps_to_bethel_string(self, open, close):

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

        return open + '-' + close

    def rotate_hours(self, sdata):
        seconds_in_two_weeks = 1209600

        next_start_date = find(sdata, 'next_start_date', False)
        if next_start_date is not None and next_start_date != '':
            # set the current hours
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
                update(sdata, 'summary', self.create_summary(sdata, 'next_') + self.create_exceptions_text(sdata))

            # if the 'next' hours are within 2 weeks, append them to the summary
            elif (datetime.datetime.strptime(next_start_date, '%m-%d-%Y') - datetime.datetime.now()).total_seconds() <= seconds_in_two_weeks:
                current_summary = self.create_summary(sdata, '', False)
                next_summary = self.create_summary(sdata, 'next_')

                title = '<p><b>New hours starting ' + next_start_date + '</b></p>'

                new_summary = current_summary + title + next_summary + self.create_exceptions_text(sdata)

                update(sdata, 'summary', new_summary)

    def create_exceptions_text(self, sdata):
        seconds_in_two_weeks = 1209600

        # add exceptions
        exceptions = find(sdata, 'exceptions')
        exceptions_text = ''

        for exception in exceptions:
            date = find(exception, 'date', False)

            if (datetime.datetime.strptime(date, '%m-%d-%Y') - datetime.datetime.now()).total_seconds() <= seconds_in_two_weeks and (datetime.datetime.strptime(date, '%m-%d-%Y') - datetime.datetime.now()).total_seconds() >= 0:
                open = find(exception, 'open', False)
                close = find(exception, 'close', False)

                exceptions_text += '<br/>on ' + date + ', ' + self.convert_timestamps_to_bethel_string(open, close)

        if exceptions_text:
            return '<p>Exceptions:<br/>' + exceptions_text + '</p>'
        else:
            return ''

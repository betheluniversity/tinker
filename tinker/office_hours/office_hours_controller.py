import datetime
import re

from flask import session
from flask import render_template
from tinker import app
from tinker.cascade_tools import *
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
        add_data['summary'] = self.create_summary(data, add_data)

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

        from copy import deepcopy

        # add_data['exceptions'].append(deepcopy(add_data['exceptions'][0]))
        # add_data['exceptions'].append(add_data['exceptions'][0])

        # todo: doesn't work if there are no existing Exceptions
        self.update_asset(data, add_data)

        return data

    def create_summary(self, data, add_data):
        week_dict = []
        week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        for week_day in week_days:
            week_day_lower = week_day.lower()
            try:
                open = find(data, week_day_lower + '_open', False)
                close = find(data, week_day_lower + '_close', False)
                chapel = add_data['closed_for_chapel']

                week_dict.append({
                    'day': week_day,
                    'time': self.convert_timestamps_to_bethel_string(open, close),
                    'chapel': chapel
                })
            except:  # if a open/close key doesn't exist, set 'Closed'
                week_dict.append({
                    'day': week_day,
                    'time': 'Closed',
                    'chapel': 'No'
                })
                continue

        summary = self.convert_week_dict_to_string(week_dict)

        return summary

    def convert_week_dict_to_string(self, week_dict):
        summary = []
        for day in week_dict:
            summary.append(day.get('day') + ': ' + day.get('time'))

        return '</br>'.join(summary)

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

        open = datetime.datetime.fromtimestamp(int(open) / 1000).strftime('%I:%M %p')
        close = datetime.datetime.fromtimestamp(int(close) / 1000).strftime('%I:%M %p')

        # if times are 12:00 -- adjust to noon or midnight
        open = self.convert_to_noon_or_midnight(open)
        close = self.convert_to_noon_or_midnight(close)

        # if :00 -- remove it
        open = open.replace(':00', '')
        close = close.replace(':00', '')

        # if times are both am/pm -- remove am/pm on first
        if ('AM' in open and 'AM' in close) or ('PM' in open and 'PM' in close):
            open = open.replace(' AM', '').replace(' PM', '')

        # convert AM to a.m. and PM to p.m
        open = self.convert_ampm(open)
        close = self.convert_ampm(close)

        return open + ' - ' + close

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

    def load_office_hours_block(self, block_id=None):

        multiple = ['exceptions']
        if not block_id:
            block_id = app.config['OFFICE_HOURS_STANDARD_BLOCK']
            multiple = []

        block = self.read_block(block_id)
        data, mdata, sdata = block.read_asset()

        edit_data = self.get_edit_data(sdata, mdata,  multiple=multiple)
        return edit_data, sdata, mdata

    def get_add_data(self, lists, form):

        # A dict to populate with all the interesting data.
        add_data = {}

        add_data['exceptions'] = []

        # handle exceptions
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

                add_data['exceptions'].append({'date': date, 'open': open, 'close': close})

            except KeyError:
                break

        for key in form.keys():
            value = form.get(key)
            if not value:
                continue

            if 'open' in key or 'close' in key and key not in ['next_closed_for_chapel']:
                value = self.date_to_java_unix(value)

            if 'date' in key:
                # form is returning default format even though it was overridden.
                # so, translate to date and then back into Cascade format.
                date = datetime.datetime.strptime(value, '%m/%d/%Y')
                value = date.strftime('%m-%d-%Y')

            key = key.replace('-', '_')

            # todo is this needed?
            if 'exceptions' in key:

                key = key.split('exceptions_')[1]

                if 'exceptions' not in add_data.keys():
                    add_data['exceptions'] = [{}]
                add_data['exceptions'][0][key] = value

            elif key in lists:
                add_data[key] = form.getlist(key)
            else:
                add_data[key] = value

        return add_data

    def update_structure(self, data, rform):

        add_data = self.get_add_data([''], rform)
        add_data['summary'] = self.create_summary(data, add_data)

        from copy import deepcopy

        # add_data['exceptions'].append(deepcopy(add_data['exceptions'][0]))
        # add_data['exceptions'].append(add_data['exceptions'][0])
        # add_data['exceptions'].append(add_data['exceptions'][0])

        # todo: doesn't work if there are no existing Exceptions
        self.update_asset(data, add_data)

        return data

    # todo: make this only do it for current. Write another method to replace current with next
    def create_summary(self, data, add_data):
        week_dict = []
        week_days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

        # todo: maybe try to add the group separating stuff here
        # build week_dict
        if datetime.datetime.now() <= datetime.datetime.strptime(add_data['next_start_date'], '%m-%d-%Y'):
            # next
            for week_day in week_days:
                try:
                    open = add_data['next_' + week_day + '_open']
                    close = add_data['next_' + week_day + '_close']
                    week_dict.append({
                        'open': self.timestamp_to_bethel_string(open),
                        'close': self.timestamp_to_bethel_string(close),
                        'string_comparer': open + close
                    })
                except:  # if a open/close key doesn't exist, set 'Closed'
                    week_dict.append({
                        'other': 'Closed',
                        'string_comparer': 'Closed'
                    })
                    continue
        else:
            # current
            for week_day in week_days:
                try:
                    open = find(data,  week_day + '_open', False)
                    close = find(data, week_day + '_close', False)
                    week_dict.append({
                        'open': self.timestamp_to_bethel_string(open),
                        'close': self.timestamp_to_bethel_string(close),
                        'string_comparer': open + close
                    })
                except:  # if a open/close key doesn't exist, set 'Closed'
                    week_dict.append({
                        'other': 'Closed',
                        'string_comparer': 'Closed'
                    })
                    continue

        # group categories together
        keys_already_used = []
        day_groupings = []
        current_grouping = []
        for index, week_day in enumerate(week_dict):
            if index not in keys_already_used:
                current_grouping.append(index)
                keys_already_used.append(index)
                for inner_index, inner_week_day in enumerate(week_dict):
                    if index < inner_index:
                        try:
                            if week_dict[index]['string_comparer'] == week_dict[inner_index]['string_comparer']:
                                current_grouping.append(inner_index)
                                keys_already_used.append(inner_index)
                        except:
                            continue
            if len(current_grouping) > 0:
                day_groupings.append(current_grouping)
                current_grouping = []

        # create summary
        summary = ''
        for grouping in day_groupings:
            day_array = []
            for item in grouping:
                day = self.convert_index_to_day(item)
                day_array.append(day)

            summary = summary + self.format_days(day_array) + ': ' + self.format_date_groupings(week_dict[grouping[0]]) + '</br>'

        return summary

    # todo: do what tim decides
    def format_days(self, day_array):
        return ', '.join(day_array)

    def format_date_groupings(self, date_object):
        if 'other' in date_object:
            return date_object['other']
        else:
            return date_object['open'] + ' - ' + date_object['close']

    # todo: do we want any other date formating stuff?
    def convert_ampm(self, date):
        return date.replace('AM', 'a.m.').replace('PM', 'p.m.')

    def timestamp_to_bethel_string(self, timestamp):
        date = datetime.datetime.fromtimestamp(int(timestamp) / 1000).strftime('%I:%M %p')
        return self.convert_ampm(date)

    def convert_index_to_day(self, index):
        day_of_week = [
            'Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday',
            'Sunday',
        ]

        return day_of_week[index]

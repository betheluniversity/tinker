import datetime
import re

from flask import session
from flask import render_template
from tinker import app
from tinker.cascade_tools import *

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

        if not block_id:
            block_id = app.config['OFFICE_HOURS_STANDARD_BLOCK']

        block = self.read_block(block_id)
        data, mdata, sdata = block.read_asset()
        edit_data = self.get_edit_data(data)
        return edit_data, mdata, sdata

    def get_add_data(self, lists, form):

        # A dict to populate with all the interesting data.
        add_data = {}

        for key in form.keys():

            value = form.get(key)
            if not value:
                continue

            if 'open' in key or 'close' in key and key not in ['next-closed_for_chapel']:
                value = self.date_to_java_unix(value)

            if 'date' in key:
                # form is returning default format even though it was overridden.
                # so, translate to date and then back into Cascade format.
                date = datetime.datetime.strptime(value, '%Y-%m-%d')
                value = date.strftime('%m-%d-%Y')

            key = key.replace('-', '_')

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

    def update_structure(self, data, rform, block_id):

        add_data = self.get_add_data([''], rform)

        from copy import deepcopy

        # add_data['exceptions'].append(deepcopy(add_data['exceptions'][0]))
        # add_data['exceptions'].append(add_data['exceptions'][0])
        # add_data['exceptions'].append(add_data['exceptions'][0])

        self.update_asset(data, add_data)

        return data
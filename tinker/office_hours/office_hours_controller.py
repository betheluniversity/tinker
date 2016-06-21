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

    # todo should this be in base controller?
    def get_add_data(self, lists, form):

        # A dict to populate with all the interesting data.
        add_data = {}

        for key in form.keys():

            value = form.get(key)
            if not value:
                continue
            key = key.replace('-', '_')

            split_key = key.split('-')
            prefix = split_key[0]

            if '_open' in key or '_close' in key:
                date = self.date_to_java_unix(value)
                add_data[key] = date

            elif 'start_date' in key:
                # form is returnint default format even though it was overridden.
                # so, translate to date and then back into Cascade format.
                date = datetime.datetime.strptime(value, '%Y-%m-%d')
                date = date.strftime('%m-%d-%Y')
                add_data[key] = date

            elif prefix in ['exceptions']:
                if prefix not in add_data.keys():
                    add_data[prefix] = {}
                add_data[prefix][split_key[1]] = form.get(key)
            elif key in lists:
                add_data[key] = form.getlist(key)
            else:
                add_data[key] = value

        # Create the system-name from title, all lowercase
        # system_name = add_data['title'].lower().replace(' ', '-')

        # Now remove any non a-z, A-Z, 0-9
        # system_name = re.sub(r'[^a-zA-Z0-9-]', '', system_name)

        # add_data['system_name'] = system_name

        return add_data

    def update_structure(self, data, rform, block_id):

        add_data = self.get_add_data([''], rform)

        self.update_asset(data, add_data)

        return data
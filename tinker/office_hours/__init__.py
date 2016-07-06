import re

from flask import Blueprint, render_template, session, url_for, redirect, request
from flask.ext.classy import FlaskView, route
from flask import json as fjson

from tinker import app
from tinker.office_hours.office_hours_controller import OfficeHoursController
from tinker.office_hours.forms import OfficeHoursForm

# todo: remove all references to this (these should all be in cascade connector)
from tinker.web_services import *


OfficeHoursBlueprint = Blueprint('office-hours', __name__, template_folder='templates')


class OfficeHoursView(FlaskView):
    route_base = '/office-hours'

    def __init__(self):
        self.base = OfficeHoursController()

    def before_request(self, name, **kwargs):
        pass

    def post(self):
        rform = request.form

        failed = self.base.validate_form(rform)
        if failed:
            return failed

        block_id = rform.get('block_id')

        block = self.base.read_block(block_id)

        data, mdata, sdata = block.read_asset()
        asset = self.base.update_structure(data, rform, block_id)
        resp = str(block.edit_asset(asset))
        self.base.log_sentry("Office Hour  Submission", resp)

        # return "edit confirm"

        return redirect(url_for('office-hours.OfficeHoursView:index', status='edit'), code=302)

    def index(self):

        username = session['username']

        forms = self.base.traverse_xml(app.config['OFFICE_HOURS_URL'], 'system-block')

        return render_template('index.html', **locals())

    def edit(self, block_id):

        edit_data, mdata, sdata = self.base.load_office_hours_block(block_id=block_id)
        standard_edit_data, m, s = self.base.load_office_hours_block()

        exceptions_new = {}
        for key, value in edit_data['exceptions'].iteritems():
            if not value:
                edit_data['exceptions'][key] = ''

            exceptions_new['exceptions_'+key] = edit_data['exceptions'][key]
            exceptions_new[key] = edit_data['exceptions'][key]

        edit_data['exceptions'] = exceptions_new

        form = OfficeHoursForm(**edit_data)

        return render_template('office-hours-form.html', **locals())

OfficeHoursView.register(OfficeHoursBlueprint)

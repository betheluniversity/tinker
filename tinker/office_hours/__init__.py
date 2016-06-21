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
        block_id = rform.get('block_id')

        block = self.base.read_block(block_id)

        data, mdata, sdata = block.read_asset()
        asset = self.base.update_structure(data, rform, block_id)
        resp = str(block.edit_asset(asset))
        self.base.log_sentry("Office Hour  Submission", resp)

        return "edit confirm"

        # return redirect(url_for('office-hours.OfficeHoursView:confirm', status='edit'), code=302)

    def index(self):

        username = session['username']
        return render_template('index.html', **locals())

    def edit(self, block_id):

        block = self.base.read_block(block_id)
        data, mdata, sdata = block.read_asset()
        edit_data = self.base.get_edit_data(data)

        for key, value in edit_data['next'].iteritems():
            if not value:
                edit_data['next'][key] = ''

        for key, value in edit_data['exceptions'].iteritems():
            if not value:
                edit_data['exceptions'][key] = ''

        edit_data['next']['next_start_date'] = edit_data['next']['next_start_date'].strftime('%m-%d-%Y')

        form = OfficeHoursForm(**edit_data)

        return render_template('office-hours-form.html', **locals())

OfficeHoursView.register(OfficeHoursBlueprint)

import re

from flask import Blueprint, render_template, session, url_for, redirect, request
from flask.ext.classy import FlaskView, route
from flask import json as fjson

from tinker import app
from tinker.e_announcements.e_announcements_base import EAnnouncementsBase

# todo: remove all references to this (these should all be in cascade connector)
from tinker.web_services import *


EAnnouncementsBlueprint = Blueprint('e-announcements', __name__, template_folder='templates')


class EAnnouncementsView(FlaskView):
    route_base = '/e-announcement'

    def __init__(self):
        self.base = EAnnouncementsBase()

    def before_request(self, name, **kwargs):
        # todo do this
        print 'e-ann before request'

    def index(self):

        username = session['username']
        forms = self.base.traverse_xml(app.config['E_ANN_URL'], 'system-block')

        # todo why reverse twice?
        forms.sort(key=lambda item:item['first_date'], reverse=True)
        forms = reversed(forms)
        return render_template('e-announcements-home.html', **locals())

    def delete(self, block_id):
        # Todo: check if user should have access to delete the block, before deleting

        self.base.delete(block_id, 'block')
        self.base.publish(app.config['E_ANNOUNCEMENTS_XML_ID'])

        return render_template('e-announcements-delete-confirm.html', **locals())

    def new(self):

        from forms import EAnnouncementsForm
        form = EAnnouncementsForm()
        new_form = True

        # todo can the tempalte access this directly?
        brm = self.base.brm

        return render_template('e-announcements-form.html', **locals())

    def confirm(self, new_or_edit):
        return render_template('e-announcements-confirm-new.html', **locals())

    @route('/in-workflow')
    def asset_is_in_workflow(self):
        return render_template('e-announcements-in-workflow.html')

    def edit(self, e_announcement_id):
        if self.base.asset_in_workflow(e_announcement_id, asset_type='block'):
            # todo is it better to just render the template here instead of redirect
            return redirect(url_for('e-announcements.EAnnouncementsView:asset_is_in_workflow'), code=302)

        from tinker.e_announcements.forms import EAnnouncementsForm

        # Get the event data from cascade
        block = self.base.read_block(e_announcement_id)
        e_announcement_data, mdata, sdata = block.read_asset()

        edit_data = self.base.get_edit_data(e_announcement_data)
        form = EAnnouncementsForm(**edit_data)
        form.e_announcement_id = e_announcement_id

        # todo can the template access this directly?
        brm = self.base.brm

        return render_template('e-announcements-form.html', **locals())

    def post(self):

        rform = request.form
        eaid = rform.get('e_announcement_id')

        if not eaid:
            bid = app.config['E_ANN_BASE_ASSET']
            e_announcement_data, mdata, sdata = self.base.cascade_connector.load_base_asset_by_id(bid, 'block')
            # hard code some things to test
            e_announcement_data['xhtmlDataDefinitionBlock']['parentFolderPath'] = '/_testing/jmo'

        else:
            block = self.base.read_block(eaid)
            e_announcement_data, mdata, sdata = block.read_asset()

        self.base.validate_form(rform)

        # Get all the form data
        asset = self.base.update_structure(e_announcement_data, rform, e_announcement_id=eaid)

        # todo this should go in EABase, but should it be in update_structure or something else?
        if eaid:
            resp = str(block.edit_asset(asset))
            self.base.log_sentry("E-Announcement edit submission", resp)
            return redirect('/e-announcement/edit/confirm', code=302)
        else:
            resp = str(self.base.create_block(asset))
            self.base.log_sentry('New e-announcement submission', resp)
            return redirect('/e-announcement/new/confirm', code=302)

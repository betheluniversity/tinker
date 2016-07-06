# TODO: clean up these unused imports
import re

from flask import Blueprint, render_template, url_for, redirect, request
from flask.ext.classy import FlaskView

from tinker.e_announcements.e_announcements_controller import EAnnouncementsController

# todo: remove all references to this (these should all be in cascade connector)
from tinker.web_services import *

# TODO: is this blueprint now redundant now that we're using Flask Classy? -- no. i think its needed?
EAnnouncementsBlueprint = Blueprint('e-announcements', __name__, template_folder='templates')


class EAnnouncementsView(FlaskView):
    route_base = '/e-announcement'

    def __init__(self):
        self.base = EAnnouncementsController()

    # currently not used
    def before_request(self, name, **kwargs):
        pass

    def index(self):
        forms = self.base.traverse_xml(app.config['E_ANN_URL'], 'system-block')

        forms.sort(key=lambda item: item['first_date'], reverse=False)
        return render_template('ea-home.html', **locals())

    def delete(self, block_id):
        # must have access to delete
        if session['username'] not in app.config['E_ANN_ADMINS']:
            return redirect(url_for('e-announcements.EAnnouncementsView:index'), code=302)

        self.base.delete(block_id, 'block')
        self.base.publish(app.config['E_ANNOUNCEMENTS_XML_ID'])

        return render_template('delete-confirm.html', **locals())

    def new(self):
        from forms import EAnnouncementsForm
        form = EAnnouncementsForm()
        new_form = True

        # extra variable the form uses
        brm = self.base.brm
        return render_template('form.html', **locals())

    def confirm(self, status='new'):
        return render_template('confirm.html', **locals())

    def edit(self, e_announcement_id):
        from tinker.e_announcements.forms import EAnnouncementsForm

        # if its in the workflow, give a warning
        if self.base.asset_in_workflow(e_announcement_id, asset_type='block'):
            return render_template('in-workflow.html')

        # Get the e-ann data from cascade
        block = self.base.read_block(e_announcement_id)
        e_announcement_data, mdata, sdata = block.read_asset()
        edit_data = self.base.get_edit_data(e_announcement_data)

        self.base.set_readonly_values(edit_data)
        form = EAnnouncementsForm(**edit_data)

        # extra variable the form uses
        brm = self.base.brm
        return render_template('form.html', **locals())

    def post(self):

        rform = request.form
        eaid = rform.get('e_announcement_id')

        failed = self.base.validate_form(rform)
        if failed:
            return failed

        if not eaid:
            bid = app.config['E_ANN_BASE_ASSET']
            e_announcement_data, mdata, sdata = self.base.cascade_connector.load_base_asset_by_id(bid, 'block')
            asset = self.base.update_structure(e_announcement_data, sdata, rform, e_announcement_id=eaid)
            resp = self.base.create_block(asset)
            self.base.log_sentry('New e-announcement submission', resp)
        else:
            block = self.base.read_block(eaid)
            e_announcement_data, mdata, sdata = block.read_asset()
            asset = self.base.update_structure(e_announcement_data, sdata, rform, e_announcement_id=eaid)
            resp = str(block.edit_asset(asset))
            self.base.log_sentry("E-Announcement edit submission", resp)

        return render_template('confirm.html', **locals())

EAnnouncementsView.register(EAnnouncementsBlueprint)

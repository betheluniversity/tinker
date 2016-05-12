__author__ = 'ces55739'

from flask import Blueprint, render_template, session, url_for, redirect, request
from flask.ext.classy import FlaskView, route
from flask import json as fjson


import re

import datetime

from tinker import app
from tinker.BaseViewTools import BaseViewTools
from tinker.e_announcements_new.banner_roles_mapping import get_banner_roles_mapping
from tinker.e_announcements_new.e_announcements_new_helper import EAnnouncementHelper

# Todo: remove all references to this (these should all be in cascade connector)
from tinker.web_services import *


NewEAnnouncementsBlueprint = Blueprint('new-e-announcement', __name__, template_folder='templates')


class NewEAnnouncementsView(FlaskView):
    route_base = '/e-announcement'

    def __init__(self):
        self.tools = BaseViewTools()
        self.helper = EAnnouncementHelper()

    def index(self):
        forms = []
        username = session['username']
        username = 'cerntson'

        forms = self.tools.traverse_xml(self.helper.inspect_child, 'http://staging.bethel.edu/_shared-content/xml/e-announcements.xml', 'system-block')

        # todo why reverse twice?
        forms.sort(key=lambda item:item['first_date'], reverse=True)
        forms = reversed(forms)
        return render_template('e-announcements-home2.html', **locals())

    def delete(self, block_id):
        # Todo: check if user should have access to delete the block, before deleting

        self.tools.delete(block_id, 'block')
        self.tools.publish(app.config['E_ANNOUNCEMENTS_XML_ID'], 'page')

        return render_template('e-announcements-delete-confirm.html', **locals())

    def new(self):
        # import this here so we dont load all the content from cascade during homepage load
        from forms import EAnnouncementsForm
        form = EAnnouncementsForm()
        new_form = True

        # bring in the mapping
        banner_roles_mapping = get_banner_roles_mapping()

        return render_template('e-announcements-form.html', **locals())

    def confirm(self, new_or_edit):
        return render_template('e-announcements-confirm-new.html', **locals())

    def asset_in_workflow(self):
        return render_template('e-announcements-in-workflow.html')

    def edit(self, e_announcement_id):
        # Todo: create this function in the cascade connector
        if is_asset_in_workflow(e_announcement_id, type='block'):
            return redirect(url_for('new-e-announcement.NewEAnnouncementsView:asset_in_workflow'), code=302)

        from tinker.e_announcements.forms import EAnnouncementsForm

        # Get the event data from cascade
        e_announcement_data = self.tools.cascade_connector.read(e_announcement_id, 'block')
        new_form = False

        # Get the different data sets from the response
        form_data = e_announcement_data.asset.xhtmlDataDefinitionBlock

        # the stuff from the data def
        s_data = form_data.structuredData.structuredDataNodes.structuredDataNode
        # regular metadata
        metadata = form_data.metadata
        # dynamic metadata
        dynamic_fields = metadata.dynamicFields.dynamicField
        # This dict will populate our EventForm object
        dates, edit_data = self.helper.get_announcement_data(dynamic_fields, metadata, s_data)  # Create an EventForm object with our data
        form = EAnnouncementsForm(**edit_data)
        form.e_announcement_id = e_announcement_id

        # convert dates to json so we can use Javascript to create custom DateTime fields on the form
        dates = fjson.dumps(dates)

        # bring in the mapping
        banner_roles_mapping = get_banner_roles_mapping()

        return render_template('e-announcements-form.html', **locals())

    def submit(self):
        # import this here so we dont load all the content
        # from cascade during homepage load
        from forms import EAnnouncementsForm
        form = EAnnouncementsForm()
        rform = request.form
        username = session['username']
        title = rform['title']
        title = title.lower().replace(' ', '-')
        title = re.sub(r'[^a-zA-Z0-9-]', '', title)

        if not form.validate_on_submit():
            if 'e_announcement_id' in request.form.keys():
                e_announcement_id = request.form['e_announcement_id']
            else:
                # This error came from the add form because e-annoucnements_id wasn't set
                new_form = True

            app.logger.debug(time.strftime("%c") + ": E-Announcement submission failed by  " + username + ". Submission could not be validated")

            # bring in the mapping
            banner_roles_mapping = get_banner_roles_mapping()

            return render_template('e-announcements-form.html', **locals())

        # Get all the form data
        add_data = self.helper.get_add_data(['banner_roles'], rform)
        if 'e_announcement_id' in rform:
            e_announcement_id = rform['e_announcement_id']
        else:
            e_announcement_id = None

        workflow = self.helper.get_e_announcement_publish_workflow(title)
        asset = get_e_announcement_structure(add_data, username, workflow=workflow, e_announcement_id=e_announcement_id)

        if e_announcement_id:
            resp = edit(asset)
            log_sentry("E-Announcement edit submission", resp)
            return redirect('/e-announcement/edit/confirm', code=302)
        else:
            resp = create_e_announcement(asset)

        log_sentry('New e-announcement submission', resp)

        return redirect('/e-announcement/new/confirm', code=302)

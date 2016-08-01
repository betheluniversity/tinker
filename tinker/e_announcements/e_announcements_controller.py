__author__ = 'ces55739'

import datetime

from flask import session
from flask import render_template
from tinker import app
from tinker.tinker_controller import TinkerController

BRM = [
        'CAS',
        'CAPS',
        'GS',
        'BSSP-TRADITIONAL',
        'BSSP-DISTANCE',
        'BSSD-TRADITIONAL',
        'BSSD-DISTANCE',
        'BSOE-TRADITIONAL',
        'BSOE-DISTANCE',
        'CAS',
        'CAPS',
        'GS',
        'BSSP',
        'BSSD',
        'St. Paul',
        'San Diego'
]


class EAnnouncementsController(TinkerController):

    def __init__(self):
        super(EAnnouncementsController, self).__init__()
        self.brm = BRM

    def inspect_child(self, child):

        try:
            author = child.find('author').text
        except AttributeError:
            author = None
        username = session['username']

        if (author is not None and username == author) or username in app.config['E_ANN_ADMINS']:
            try:
                return self._iterate_child_xml(child, author)
            except AttributeError:
                # not a valid e-ann block
                return None
        else:
            return None

    def _iterate_child_xml(self, child, author):

        first = child.find('system-data-structure/first-date').text
        second = child.find('system-data-structure/second-date').text
        first_date_object = datetime.datetime.strptime(first, '%m-%d-%Y')
        first_date = first_date_object.strftime('%A %B %d, %Y')
        first_date_past = first_date_object < datetime.datetime.now()

        second_date = ''
        second_date_past = ''
        if second:
            second_date_object = datetime.datetime.strptime(second, '%m-%d-%Y')
            second_date = second_date_object.strftime('%A %B %d, %Y')
            second_date_past = second_date_object < datetime.datetime.now()

        roles = []
        values = child.find('dynamic-metadata')
        for value in values:
            if value.tag == 'value':
                roles.append(value.text)

        try:
            workflow_status = child.find('workflow').find('status').text
        except AttributeError:
            workflow_status = None

        page_values = {
            'author': author,
            'id': child.attrib['id'] or "",
            'title': child.find('title').text or None,
            'created-on': child.find('created-on').text or None,
            'first_date': first_date,
            'second_date': second_date,
            'roles': roles,
            'workflow_status': workflow_status,
            'first_date_past': first_date_past,
            'second_date_past': second_date_past,
            'message': self.element_tree_to_html(child.find('system-data-structure').find('message')) or None
        }
        return page_values

    def validate_form(self, rform):

        from forms import EAnnouncementsForm;

        form = EAnnouncementsForm()

        if not form.validate_on_submit():
            if 'e_announcement_id' in rform.keys():
                e_announcement_id = rform['e_announcement_id']
            else:
                new_form = True
            # bring in the mapping
            brm = self.brm
            return render_template('form.html', **locals())

    def update_structure(self, e_announcement_data, sdata, rform, e_announcement_id=None):
        add_data = self.get_add_data(['banner_roles'], rform)

        # create workflow
        workflow = self.create_workflow(app.config['E_ANNOUNCEMENT_WORKFLOW_ID'], add_data['title'])
        self.add_workflow_to_asset(workflow, e_announcement_data)

        # if parent folder ID exists it will use that over path
        add_data['parentFolderId'] = ''
        add_data['parentFolderPath'] = self.get_e_announcement_parent_folder(add_data['first_date'])

        # add missing data and make sure its in the right format.
        add_data['name'] = session['name']
        add_data['message'] = self.escape_wysiwyg_content(add_data['message'])

        # todo, update these to have _ instead of - in Cascade so we don't have to translate
        add_data['email'] = session['user_email']
        add_data['banner-roles'] = add_data['banner_roles']
        add_data['first-date'] = add_data['first_date']
        add_data['second-date'] = add_data['second_date']

        # add id
        if e_announcement_id:
            add_data['id'] = e_announcement_id

        # todo, revert this after 'name' in the Cascade data-def is changed so it doesn't conflict (then we don't have to call update_asset twice)
        # update asset
        self.update_asset(sdata, add_data)
        add_data['name'] = add_data['title']
        self.update_asset(e_announcement_data, add_data)

        # for some reason, title is not already set, so it must be set manually
        e_announcement_data['xhtmlDataDefinitionBlock']['metadata']['title'] = add_data['title']

        # once all editing is done, move it if it needs to be moved
        if e_announcement_id:
            self.move(e_announcement_id, add_data['parentFolderPath'], type='block')

        return e_announcement_data

    # dates are set to readonly if they occur before today
    def set_readonly_values(self, edit_data):
        # print edit_data
        today = datetime.datetime.now()
        first_readonly = False
        second_readonly = False
        if edit_data['first_date'] < today:
            first_readonly = edit_data['first_date'].strftime('%A %B %d, %Y')
        if 'second_date' in edit_data and edit_data['second_date'] and edit_data['second_date'] < today:
            second_readonly = edit_data['second_date'].strftime('%A %B %d, %Y')

        edit_data['first_readonly'] = first_readonly
        edit_data['second_readonly'] = second_readonly

    def get_e_announcement_parent_folder(self, date):
        # break the date into Year/month
        split_date = date.split("-")
        month = self.convert_month_num_to_name(split_date[0])
        year = split_date[2]

        self.copy(app.config['BASE_ASSET_BASIC_FOLDER'], '/e-announcements/' + year, 'folder')
        self.copy(app.config['BASE_ASSET_BASIC_FOLDER'], '/e-announcements/' + year + "/" + month, 'folder')

        return "/e-announcements/" + year + "/" + month

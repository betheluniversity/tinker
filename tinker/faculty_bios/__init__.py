from werkzeug.utils import secure_filename

# bu-cascade
from bu_cascade.asset_tools import *

# flask
from flask import Blueprint, redirect, send_from_directory
from flask_classy import FlaskView, route
# tinker
from tinker.admin.sync.sync_metadata import data_to_add
from faculty_bio_controller import *


FacultyBiosBlueprint = Blueprint('faculty-bios', __name__, template_folder='templates')


# todo: add a before_request method
class FacultyBiosView(FlaskView):
    route_base = '/faculty-bios'

    def __init__(self):
        self.base = FacultyBioController()

    def before_request(self, name, **kwargs):
        pass

    def index(self):
        username = session['username']
        roles = session['roles']

        forms = self.base.traverse_xml(app.config['FACULTY_BIOS_XML_URL'], 'system-page')
        forms = sorted(forms, key=itemgetter('last-name'), reverse=False)

        # the faculty special admins should be able to see every bio, based on school.
        if username in app.config['FACULTY_BIOS_ADMINS']:
            show_special_admin_view = True
            show_create = True

            # This nastiness is to maintain order and have the class value
            all_schools = [
                {'cas': 'College of Arts and Sciences'},
                {'caps': 'College of Adult and Professional Studies'},
                {'gs': 'Graduate School'},
                {'sem': 'Bethel Seminary'},
                {'bu': 'Administration with Faculty Status'},
                {'other-category': 'Other'}
            ]
        else:  # normal view
            show_special_admin_view = False
            show_create = len(forms) == 0 or 'Tinker Faculty Bios' in session['groups']

        return render_template('faculty-bio-home.html', **locals())

    @route('delete/<page_id>', methods=['GET'])
    def delete(self, page_id):
        self.base.delete(page_id, "page")
        self.base.unpublish(page_id, "page")

        return redirect('/faculty-bio/delete-confirm', code=302)

    @route('/delete-confirm', methods=['GET'])
    def delete_confirm(self):
        return render_template('faculty-bio-delete-confirm.html')

    def new(self):
        # import this here so we dont load all the content
        # from cascade during homepage load
        from forms import FacultyBioForm

        form = FacultyBioForm()
        roles = session['roles']
        edit_image = self.base.should_be_able_to_edit_image(roles)
        metadata = fjson.dumps(data_to_add)
        add_form = True

        return render_template('faculty-bio-form.html', **locals())

    def confirm(self):
        return render_template('faculty-bio-confirm.html')

    @route('/in-workflow', methods=['GET'])
    def faculty_bio_in_workflow(self):
        return render_template('faculty-bio-in-workflow.html')

    def edit(self, faculty_bio_id):
        # if the event is in a workflow currently, don't allow them to edit. Instead, redirect them.
        if self.base.asset_in_workflow(faculty_bio_id):
            return redirect('/faculty-bio/in-workflow', code=302)

        from forms import FacultyBioForm
        form = FacultyBioForm()

        roles = session['roles']

        page = self.base.read_page(faculty_bio_id)
        faculty_bio_data, mdata, sdata = page.read_asset()
        edit_data = self.base.get_edit_data(sdata, mdata, ['education', 'job-titles'])

        # pull the group data to the top level of the dict
        group_identifiers = ['add_to_bio', 'expertise']
        for identifier in group_identifiers:
            for key, value in edit_data[identifier].iteritems():
                edit_data[key] = value

        # turn the image into the correct identifier
        edit_data['image_url'] = edit_data['image']

        edit_image = self.base.should_be_able_to_edit_image(roles)

        # Create an EventForm object with our data
        form = FacultyBioForm(**edit_data)

        # convert job titles and degrees to json so we can use Javascript to create custom DateTime fields on the form
        new_job_titles = fjson.dumps(edit_data['job-titles'])
        degrees = fjson.dumps(edit_data['education'])

        # pre-filled metadata for job titles
        metadata = fjson.dumps(data_to_add)

        return render_template('faculty-bio-form.html', **locals())

    @route('/submit', methods=['POST'])
    def submit(self):

        rform = request.form
        username = session['username']
        groups = session['groups']

        faculty_bio_id = rform.get('faculty_bio_id')

        failed = self.base.validate_form(rform)
        if failed:
            return failed

        if faculty_bio_id:
            # existing bio
            page = self.base.read_page(faculty_bio_id)
            page_asset, mdata, sdata, = page.read_asset()
            new_asset = self.base.update_structure(page_asset, sdata, rform, faculty_bio_id=faculty_bio_id)
            resp = page.edit_asset(new_asset)

            self.base.log_sentry("Faculty bio edit submission", resp)
            status = 'edit'
        else:
            # new bio
            base_asset_id = app.config['FACULTY_BIOS_BASE_ASSET']
            faculty_bio_data, mdata, sdata = self.base.cascade_connector.load_base_asset_by_id(base_asset_id, 'page')
            asset = self.base.update_structure(faculty_bio_data, sdata, rform, faculty_bio_id=faculty_bio_id)
            resp = self.base.create_page(asset)
            faculty_bio_id = resp.asset['page']['id']

            self.base.log_sentry("Faculty bio new submission", resp)
            status = 'new'

        self.base.publish(app.config['FACULTY_BIOS_XML_ID'])
        return render_template('faculty-bio-confirm.html', **locals())

    @route('/activate', methods=['post'])
    def activate(self):
        data = json.loads(request.data)
        faculty_bio_id = data['id']
        activate_page = data['activate']

        page = self.base.read_page(faculty_bio_id)
        asset, md, sd = page.get_asset()

        # activate bio
        if activate_page == 'activate':
            update(sd, 'deactivate', 'No')
            page.edit_asset(asset)
            page.publish_asset()
        else:  # deactivate bio
            update(sd, 'deactivate', 'Yes')
            page.edit_asset(asset)
            page.unpublish_asset()

        self.base.publish(app.config['FACULTY_BIOS_XML_ID'])

        return 'Success'

    def edit_all(self):
        type_to_find = 'system-page'
        xml_url = app.config['FACULTY_BIOS_XML_URL']
        self.base.edit_all(type_to_find, xml_url)
        return 'success'


FacultyBiosView.register(FacultyBiosBlueprint)

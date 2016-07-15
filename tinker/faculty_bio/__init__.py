from faculty_bio_controller import *
from flask import Blueprint, redirect, send_from_directory
from flask.ext.classy import FlaskView, route
from tinker.admin.sync.sync_metadata import data_to_add
from werkzeug.utils import secure_filename

FacultyBioBlueprint = Blueprint('faculty-bio', __name__, template_folder='templates')


# todo: add a before_request method
class FacultyBioView(FlaskView):
    route_base = '/faculty-bio'

    def __init__(self):
        self.base = FacultyBioController()

    def index(self):
        username = session['username']
        roles = get_roles(username)

        # todo: call the appropriate traverse_xml method in tinker controller
        # index page for adding events and things
        forms = self.base.get_faculty_bios_for_user(username)

        show_create = len(forms) == 0 or 'Tinker Faculty Bios' in session['groups']

        # return forms
        return render_template('faculty-bio-home.html', **locals())

    # todo: remove this 'route' line and use flask classy defaults
    @route('/delete/<page_id>', methods=['GET'])
    def delete_page(self, page_id):
        self.base.delete(page_id, "page")
        self.base.publish_faculty_bio_xml()

        # todo: I believe we don't need to do these anymore. Double check this, though.
        # Todo: only publish the corresponding faculty listing pages.
        # self.base.publish([app.config['FACULTY_LISTING_CAPS_ID']], 'publishset')
        # self.base.publish([app.config['FACULTY_LISTING_GS_ID']], 'publishset')
        # self.base.publish([app.config['FACULTY_LISTING_SEM_ID']], 'publishset')
        # self.base.publish([app.config['FACULTY_LISTING_CAS_ID']], 'publishset')

        return redirect('/faculty-bio/delete-confirm', code=302)

    # todo: remove this 'route' line and use flask classy defaults
    @route('/delete-confirm', methods=['GET'])
    def delete_confirm(self):
        return render_template('faculty-bio-delete-confirm.html')

    def new(self):
        # import this here so we dont load all the content
        # from cascade during homepage load
        from forms import FacultyBioForm

        form = FacultyBioForm()
        # todo: roles should be gotten from the session variable
        roles = get_roles()
        # todo: this method currently is in tools.py. This needs to be fixed
        edit_image = should_be_able_to_edit_image(roles)

        # todo: this id shouldn't have to have a default value
        faculty_bio_id = ""

        metadata = fjson.dumps(data_to_add)

        add_form = True
        return render_template('faculty-bio-form.html', **locals())

    # todo: remove this 'route' line and use flask classy defaults
    @route('/confirm-new', methods=['GET'])
    def submit_confirm_new(self):
        return render_template('faculty-bio-confirm-new.html')

    # todo: remove this 'route' line and use flask classy defaults
    @route('/confirm-edit', methods=['GET'])
    def submit_confirm_edit(self):
        return render_template('faculty-bio-confirm-edit.html')

    # todo: remove this 'route' line and use flask classy defaults
    @route('/in-workflow', methods=['GET'])
    def faculty_bio_in_workflow(self):
        return render_template('faculty-bio-in-workflow.html')

    def edit(self, faculty_bio_id):
        # if the event is in a workflow currently, don't allow them to edit. Instead, redirect them.
        if self.base.asset_in_workflow(faculty_bio_id):
            return redirect('/faculty-bio/in-workflow', code=302)

        # import this here so we dont load all the content
        # from cascade during homepage load
        from forms import FacultyBioForm

        form = FacultyBioForm()
        # todo: roles should be gotten from the session variable
        roles = get_roles()
        # todo: this method currently is in tools.py. This needs to be fixed
        edit_image = should_be_able_to_edit_image(roles)

        # todo: this method should be called from tinker_controller
        # Get the event data from cascade
        faculty_data = read(faculty_bio_id)
        # todo: these next few lines shouldn't be manual. use find and stuff to get them easier
        form_data = faculty_data.asset.page
        # the stuff from the data def
        s_data = form_data.structuredData.structuredDataNodes.structuredDataNode
        # regular metadata
        metadata = form_data.metadata
        # dynamic metadata
        dynamic_fields = metadata.dynamicFields.dynamicField
        # This dict will populate our EventForm object
        edit_data = {}

        degrees = {}
        degree_count = 0

        new_job_titles = {}
        new_job_title_count = 0

        # Start with structuredDataNodes (data def content)
        # todo: this can call get_edit_data from tinker_controller
        for node in s_data:
            node_identifier = node.identifier.replace('-', '_')
            node_type = node.type
            if node_type == "text":
                edit_data[node_identifier] = node.text

            elif node_type == 'group':
                if node_identifier == "add_to_bio" or node_identifier == "expertise":
                    for group_node in node.structuredDataNodes.structuredDataNode:
                        group_node_identifier = group_node.identifier.replace('-', '_')
                        edit_data[group_node_identifier] = group_node.text
                if node_identifier == "education":
                    for node in node.structuredDataNodes.structuredDataNode:
                        node_identifier = node.identifier.replace('-', '_')
                        if node_identifier == "add_degree":
                            degree_data = {}
                            for degree in node.structuredDataNodes.structuredDataNode:
                                degree_identifier = degree.identifier.replace('-', '_')
                                degree_data[degree.identifier] = degree.text
                            degrees[degree_count] = degree_data
                            degree_count += 1
                if node_identifier == "job_titles":
                    new_job_title_data = {}
                    for field in node.structuredDataNodes.structuredDataNode:
                        node_identifier = field.identifier.replace('-', '_')
                        new_job_title_data[node_identifier] = field.text
                    new_job_titles[new_job_title_count] = new_job_title_data
                    new_job_title_count += 1

            elif node_identifier == 'image':
                groups = get_groups_for_user()
                edit_data['image'] = node.text
                edit_data['image_url'] = node.filePath

        # now metadata dynamic fields
        for field in dynamic_fields:
            # This will fail if no metadata is set. It should be required but just in case
            if field.fieldValues:
                items = [item.value for item in field.fieldValues.fieldValue]
                edit_data[field.name.replace('-', '_')] = items

        # todo: this portion can call some method in the tinker_controller
        # Add the rest of the fields. Can't loop over these kinds of metadata
        authors = metadata.author
        try:
            authors = authors.split(", ")
            edit_data['author'] = authors[0]
        except AttributeError:
            edit_data['author'] = ''

        # Create an EventForm object with our data
        form = FacultyBioForm(**edit_data)
        form.faculty_bio_id = faculty_bio_id

        # convert job titles and degrees to json so we can use Javascript to create custom DateTime fields on the form
        new_job_titles = fjson.dumps(new_job_titles)
        degrees = fjson.dumps(degrees)

        # metadata for job titles
        metadata = fjson.dumps(data_to_add)

        return render_template('faculty-bio-form.html', **locals())

    # todo: remove this 'route' line and use flask classy defaults
    # Was submit_faculty_bio_form(), but renamed for simplification and FlaskClassy convention
    @route('/submit', methods=['POST'])
    def submit(self):
        # import this here so we dont load all the content
        # from cascade during homepage load
        from forms import FacultyBioForm
        form = FacultyBioForm()

        rform = request.form
        username = session['username']
        # todo: this can call a method in the tinker_controller
        title = rform['last'] + "-" + rform['first']
        title = title.lower().replace(' ', '-')
        title = re.sub(r'[^a-zA-Z0-9-]', '', title)

        degrees, degrees_good, num_degrees = self.base.check_degrees(rform)
        new_jobs_good, num_new_jobs = self.base.check_job_titles(rform)
        # todo: this should be separated out into a validate method
        if not form.validate_on_submit() or (not new_jobs_good or not degrees_good):
            if 'faculty_bio_id' in request.form.keys():
                faculty_bio_id = request.form['faculty_bio_id']
            else:
                # This error came from the add form because event_id wasn't set
                add_form = True

            metadata = fjson.dumps(data_to_add)
            return render_template('faculty-bio-form.html', **locals())

        # Get all the form data
        add_data = self.base.get_add_data(
            ['school', 'department', 'adult_undergrad_program', 'graduate_program', 'seminary_program'], rform)

        # todo: groups can be accessed from the session variable
        # Images
        groups = get_groups_for_user()

        # todo: this should be cleaned up
        try:
            image_name = form.image.data.filename
        except AttributeError:
            image_name = ""
        if image_name != "":
            image_name = add_data['system_name'] + '.jpg'
            image_path = secure_filename(image_name)

            form.image.data.save(app.config['UPLOAD_FOLDER'] + image_path)

            add_data['image_name'] = image_name
            add_data['image_path'] = image_path

        # End Images

        faculty_bio_id = rform['faculty_bio_id']
        if faculty_bio_id == "":
            faculty_bio_id = None

        workflow = None
        # todo: the generic get_workflow method (can be found in create-base-view branch)
        workflow = self.base.get_bio_publish_workflow(title, username, faculty_bio_id, add_data)
        asset = self.base.get_faculty_bio_structure(add_data, username, faculty_bio_id, workflow=workflow)

        if faculty_bio_id:
            # existing bio
            block = self.base.read_block(app.config['FACULTY_BIO_XML_ID'])
            resp = str(block.edit_asset(asset))
            log_sentry("Faculty bio edit submission", resp)
            # publish corresponding pubish set to make sure corresponding pages get edits
            if not workflow:
                self.base.publish(faculty_bio_id, "page")
            return render_template('faculty-bio-confirm-edit.html', **locals())
        else:
            # new bio
            resp = self.base.create_faculty_bio(asset)
            faculty_bio_id = resp.createdAssetId
            if not workflow:
                self.base.publish(faculty_bio_id, "page")
            return render_template('faculty-bio-confirm-new.html', **locals())

    # todo: remove this 'route' line and use flask classy defaults
    # Was uploaded_file(filename), but renamed for simplification and FlaskClassy convention
    @route('/uploads/<path:filename>')
    def uploads(self, filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

FacultyBioView.register(FacultyBioBlueprint)

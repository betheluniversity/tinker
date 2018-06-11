# Global
import json
import random
from operator import itemgetter

# Packages
from bu_cascade.asset_tools import find, update
from flask import abort, redirect, render_template, request, session, Response
from flask import json as fjson
from flask_classy import FlaskView, route

# Local
from tinker import app, cache
from tinker.admin.sync.sync_metadata import data_to_add
from faculty_bio_controller import FacultyBioController
# Figure out what to do with this
import csv
from tinker.tinker_controller import EncodingDict
from unidecode import unidecode

class FacultyBiosView(FlaskView):
    route_base = '/faculty-bios'

    def __init__(self):
        self.base = FacultyBioController()

    # todo: add a before_request method
    def before_request(self, name, **kwargs):
        if 'FACULTY' not in session['roles'] \
                and 'RECENT-FACULTY' not in session['roles'] \
                and 'SPONSORED-FACULTY' not in session['roles'] \
                and 'Tinker Faculty Bios' not in session['groups'] \
                and 'Tinker Faculty Bios - CAS' not in session['groups'] \
                and 'Tinker Faculty Bios - CAPS and GS' not in session['groups'] \
                and 'Tinker Faculty Bios - SEM' not in session['groups'] \
                and 'Administrators' not in session['groups'] \
                and 'Tinker Faculty Bios - Admin' not in session['groups']:
            abort(403)

    def index(self):
        username = session['username']

        @cache.memoize(timeout=600)
        def index_cache(username):
            roles = session['roles']

            forms = self.base.traverse_xml(app.config['FACULTY_BIOS_XML_URL'], 'system-page')
            forms = sorted(forms, key=itemgetter('last-name'), reverse=False)

            # the faculty special admins should be able to see every bio, based on school.
            if 'Tinker Faculty Bios - Admin' in session['groups'] or 'Administrators' in session['groups']:
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
                show_create = len(forms) == 0 \
                              or 'Tinker Faculty Bios - CAS' in session['groups'] \
                              or 'Tinker Faculty Bios - CAPS and GS' in session['groups'] \
                              or 'Tinker Faculty Bios - SEM' in session['groups'] \
                              or self.base.is_user_in_web_author_groups()

            return render_template('faculty-bios/home.html', **locals())

        return index_cache(username)

    @route('delete/<faculty_bio_id>', methods=['GET'])
    def delete(self, faculty_bio_id):
        self.base.delete(faculty_bio_id, "page")
        self.base.unpublish(faculty_bio_id, "page")

        return redirect('/faculty-bios/delete-confirm', code=302)

    @route('/delete-confirm', methods=['GET'])
    def delete_confirm(self):
        return render_template('faculty-bios/delete-confirm.html')

    def new(self):
        # import this here so we dont load all the content
        # from cascade during homepage load
        from forms import FacultyBioForm

        form = FacultyBioForm()
        roles = session['roles']
        edit_image = self.base.should_be_able_to_edit_image()
        metadata = fjson.dumps(data_to_add)
        add_form = True

        return render_template('faculty-bios/form.html', **locals())

    @cache.memoize(timeout=3600)
    def confirm(self):
        return render_template('faculty-bios/confirm.html')

    @route('/in-workflow', methods=['GET'])
    def faculty_bio_in_workflow(self):
        return render_template('faculty-bios/in-workflow.html')

    def edit(self, faculty_bio_id):
        # if the event is in a workflow currently, don't allow them to edit. Instead, redirect them.
        if self.base.asset_in_workflow(faculty_bio_id):
            return redirect('/faculty-bios/in-workflow', code=302)

        from forms import FacultyBioForm
        form = FacultyBioForm()

        roles = session['roles']

        page = self.base.read_page(faculty_bio_id)
        faculty_bio_data, mdata, sdata = page.read_asset()
        edit_data = self.base.get_edit_data(sdata, mdata, ['education', 'job-titles'])
        edit_data['author_faculty'] = find(mdata, 'author', False)
        # turn the image into the correct identifier
        try:
            edit_data['image_url'] = edit_data['image']
        except:
            edit_data['image_url'] = ''
        edit_image = self.base.should_be_able_to_edit_image()

        # pull the add_to_bio data up one level
        for key, value in edit_data['add_to_bio'].iteritems():
            edit_data[key] = value

        # Create an EventForm object with our data
        form = FacultyBioForm(**edit_data)

        # convert job titles and degrees to json so we can use Javascript to create custom DateTime fields on the form
        new_job_titles = fjson.dumps(edit_data['job-titles'])
        degrees = fjson.dumps(edit_data['education'])

        # pre-filled metadata for job titles
        metadata = fjson.dumps(data_to_add)

        return render_template('faculty-bios/form.html', **locals())

    @route('/submit', methods=['POST'])
    def submit(self):
        rform = self.base.dictionary_encoder.encode(request.form)
        username = session['username']
        groups = session['groups']

        faculty_bio_id = rform.get('faculty_bio_id')

        validated_form = self.base.validate_form(rform.internal_dictionary())
        if bool(validated_form.errors):  # Evaluates to False if there are no entries in the dictionary of errors
            if 'faculty_bio_id' in request.form.keys():
                faculty_bio_id = request.form['faculty_bio_id']
            else:
                # This error came from the add form because event_id wasn't set
                add_form = True

            form = validated_form
            add_data = self.base.get_add_data(['faculty_location'], rform)
            metadata = fjson.dumps(data_to_add)
            new_job_titles = fjson.dumps(self.base.get_job_titles(add_data))
            degrees = fjson.dumps(self.base.get_degrees(add_data))
            return render_template('faculty-bios/form.html', **locals())

        if faculty_bio_id:
            # existing bio
            page = self.base.read_page(faculty_bio_id)
            page_asset, mdata, sdata, = page.read_asset()
            new_asset = self.base.update_structure(page_asset, sdata, rform, faculty_bio_id=faculty_bio_id)
            resp = page.edit_asset(new_asset)
            self.base.cascade_call_logger(locals())
            self.base.log_sentry("Faculty bio edit submission", resp)
            status = 'edit'
        else:
            # new bio
            base_asset_id = app.config['FACULTY_BIOS_BASE_ASSET']
            faculty_bio_data, mdata, sdata = self.base.cascade_connector.load_base_asset_by_id(base_asset_id, 'page')
            asset = self.base.update_structure(faculty_bio_data, sdata, rform, faculty_bio_id=faculty_bio_id)
            resp = self.base.create_page(asset)
            faculty_bio_id = resp.asset['page']['id']
            self.base.cascade_call_logger(locals())
            self.base.log_sentry("Faculty bio new submission", resp)
            status = 'new'

        self.base.publish(app.config['FACULTY_BIOS_XML_ID'])
        return render_template('faculty-bios/confirm.html', **locals())

    @route('/activate', methods=['post'])
    def activate(self):
        data = self.base.dictionary_encoder.encode(json.loads(request.data))
        faculty_bio_id = data['id']
        activate_page = data['activate']

        page = self.base.read_page(faculty_bio_id)
        asset, md, sd = page.get_asset()

        # activate bio
        if activate_page == 'activate':
            update(sd, 'deactivate', 'No')
            asset['page']['shouldBePublished'] = True
            page.edit_asset(asset)
            page.publish_asset()
        else:  # deactivate bio
            update(sd, 'deactivate', 'Yes')
            page.unpublish_asset()
            asset['page']['shouldBePublished'] = False
            page.edit_asset(asset)

        self.base.publish(app.config['FACULTY_BIOS_XML_ID'])

        return 'Success'

    def edit_all(self):
        type_to_find = 'system-page'
        xml_url = app.config['FACULTY_BIOS_XML_URL']
        self.base.edit_all(type_to_find, xml_url)
        return 'success'

    @route("/faculty-bio-info-test")
    def getFacultyBioTest(self):
        test_form = self.base.traverse_xml(app.config['FACULTY_BIOS_XML_URL'], 'system-page', True, True)

        # for data in test_form:
        #     my_list = []
        #     for key in data:
        #         my_list.append(unidecode(data[key]))
        #     print my_list

        #648

        # for data in test_form:
        #     print([data['first'], data['last'], data['author'], data['location'], unidecode(data['highlight']),
        #            "job title", data['email'], data['started-at-bethel'], "degree 1", "degree 2",
        #            unidecode(data['biography']), 'courses'])

        with open('faculty-info.csv', 'w') as csvfile:
            filewriter = csv.writer(csvfile)
            filewriter.writerow(['Faculty first name', 'Faculty last name', 'Faculty member\'s username', 'Location',
                                 'Highlight text', 'Job Title 1', 'Email', 'Started at Bethel in', 'Degree 1','Degree 2',
                                 'Biography', 'Courses Taught', 'Awards', 'Publications', 'Certificates and licenses',
                                 'Professional Organizations, Committees, and Boards', 'Hobbies and interests',
                                 'Areas of expertise', 'Research interests', 'Teaching specialty', 'Quote',
                                 'Professional website or blog'])

            # for data in test_form:
            #     my_list = []
            #     for key in data:
            #         my_list.append(unidecode(data[key]))
            #     filewriter.writerow(my_list)

            for data in test_form:
                filewriter.writerow([unidecode(data['first']), unidecode(data['last']),
                                     unidecode(data['author']),
                                     # "author",
                                     unidecode(data['location']),
                                     unidecode(data['highlight']),
                                     unidecode(data['job-titles']),
                                     # "job title",
                                     unidecode(data['email']),
                                     # "email",
                                     unidecode(data['started-at-bethel']),
                                     unidecode(data['education']),
                                     # "degree 1", "degree 2",
                                     unidecode(data['biography']),
                                     unidecode(data['courses']),
                                     unidecode(data['awards']),
                                     unidecode(data['publications']),
                                     unidecode(data['certificates']),
                                     unidecode(data['organizations']),
                                     unidecode(data['hobbies']),
                                     unidecode(data['areas']),
                                     unidecode(data['research-interests']),
                                     unidecode(data['teaching-specialty']),
                                     unidecode(data['quote']),
                                     unidecode(data['website'])
                                    ])

        with open('faculty-info.csv', 'rb') as f:
            return Response(
                f.read(),
                mimetype="text/csv",
                headers={"Content-disposition":
                            "attachment; filename=faculty-bio-info.csv"})


# 'first': child.find('.//first').text,
# 'last': child.find('.//last').text,
# 'author': child.find('author').text,
# 'location': child.find('.//faculty_location/value').text,
# 'highlight': child.find('.//highlight').text or "",
# 'job-titles': child.find('job-titles').text,
# 'email': child.find('.//email').text,
# 'started-at-bethel': child.find('.//started-at-bethel').text,
# 'education': child.find('education'),
# 'biography': child.find('biography'),
# 'courses': child.find('courses'),
# 'awards': child.find('awards'),
# 'publications': child.find('publications'),
# 'certificates': child.find('certificates'),
# 'organizations': child.find('organizations'),
# 'hobbies': child.find('hobbies'),
# 'areas': child.find('areas'),
# 'research-interests': child.find('research-interests'),
# 'teaching-specialty': child.find('teaching-specialty'),
# 'quote': child.find('quote'),
# 'website': child.find('website')
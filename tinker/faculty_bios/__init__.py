# Global
import json
import random
from operator import itemgetter

# Packages
from bu_cascade.asset_tools import find, update
from flask import abort, redirect, render_template, request, session, Response
from flask import json as fjson
from flask_classy import FlaskView, route
import csv
from unidecode import unidecode

# Local
from tinker import app, cache
from tinker.admin.sync.sync_metadata import data_to_add
from faculty_bio_controller import FacultyBioController


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

    @route("/faculty-bio-csv")
    def get_faculty_bio_csv(self):

        if 'Administrators' not in session['groups'] or 'Tinker Faculty Bios - Admin' not in session['groups']:
            abort(403)

        # Traverses the xml file
        info_form = self.base.traverse_xml(app.config['FACULTY_BIOS_XML_URL'], 'system-page', True, True)

        # Opens the xml file and signifies that we will write to it
        with open('faculty-info.csv', 'w') as csvfile:

            filewriter = csv.writer(csvfile)

            # # Adds column headers to the list
            my_list = ['Faculty first name', 'Faculty last name', 'Faculty member\'s username', 'Location',
            #            'Highlight text'
                       ]

            max_jobs = 0
            max_edu = 0
            # Gets the maximum number of jobs and maximum number of educations out of everyone
            for data in info_form:
                if data['max-jobs'] > max_jobs:
                    max_jobs = data['max-jobs']
                if data['max-edu'] > max_edu:
                    max_edu = data['max-edu']

            # Creates max_jobs spaces for jobs and adds them to the list
            for i in range(1, max_jobs + 1):
                my_list.append('Job Title ' + str(i))
                my_list.append('Job Title-School ' + str(i))
                my_list.append('Job Title-Department ' + str(i))
            #
            # my_list.extend(['Email', 'Started at Bethel in'])

            # Creates max_edu spaces for educations and adds them to the list
            for j in range(1, max_edu + 1):
                my_list.append('Degree-Earned ' + str(j))
                my_list.append('Degree-School ' + str(j))
                my_list.append('Degree-Year ' + str(j))

            # Adds the remaining column headers to the list
            my_list.extend(['Biography', 'Courses Taught', 'Awards', 'Publications', 'Presentations',
                            'Certificates and licenses', 'Professional Organizations, Committees, and Boards',
                            'Hobbies and interests', 'Areas of expertise', 'Research interests', 'Teaching specialty',
                            'Quote', 'Professional website or blog'])

            # # Writes the "header" of the csv file signify what data is held in that column
            filewriter.writerow(my_list)

            # Now we will iterate through all the faculty and make a row dedicated to each of them following the
            # format specified by the header
            for data in info_form:

                row_list = [unidecode(data['first']), unidecode(data['last']), unidecode(data['author']),
                            unidecode(data['location']),
                            # unidecode(data['highlight'])
                            ]

                for i in range(1, max_jobs + 1):
                    if ('school' + str(i)) in data.keys():
                        job_title = unidecode(str(data['job_title' + str(i)]))
                        school = unidecode(str(data['school' + str(i)]))
                        department = unidecode(str(data['department' + str(i)]))
                    else:
                        school = ""
                        department = ""
                        job_title = ""
                    row_list.extend([job_title, school, department])

                # row_list.extend([unidecode(data['email']), unidecode(data['started-at-bethel'])])

                for j in range(1, max_edu + 1):
                    if ('school-edu' + str(j)) in data.keys():
                        edu_school = unidecode(str(data['school-edu' + str(j)]))
                        degree_earned = unidecode(str(data['degree-earned' + str(j)]))
                        year = unidecode(str(data['year' + str(j)]))
                    else:
                        edu_school = ""
                        degree_earned = ""
                        year = ""
                    row_list.extend([degree_earned, edu_school, year])

                row_list.extend([unidecode(data['biography']), unidecode(data['courses']), unidecode(data['awards']),
                                 unidecode(data['publications']), unidecode(data['presentations']),
                                 unidecode(data['certificates']), unidecode(data['organizations']),
                                unidecode(data['hobbies']),
                                 # unidecode(data['areas']),
                #                  unidecode(data['research-interests']), unidecode(data['teaching-specialty']),
                #                  unidecode(data['quote']), unidecode(data['website'])
                                 ])

                # Writes each faculty a row of data
                filewriter.writerow(row_list)

        # Opens the file and signifies that we will read it
        with open('faculty-info.csv', 'rb') as f:
            # returns a Response (so the file can be downloaded)
            return Response(
                f.read(),
                mimetype="text/csv",
                headers={"Content-disposition":
                            "attachment; filename=faculty-bio-info.csv"})
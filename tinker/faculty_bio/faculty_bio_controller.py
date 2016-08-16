import json
import re
import urllib2

from operator import itemgetter
from tinker.cascade_tools import *
from tinker.tinker_controller import Cascade
from xml.etree import ElementTree
from tinker.tinker_controller import *
from tinker.admin.sync.sync_metadata import data_to_add


class FacultyBioController(TinkerController):
    # todo: this is better, but it still needs a little work
    def inspect_child(self, child):
        try:
            author = child.find('author').text
        except AttributeError:
            author = None

        username = session['username']
        groups = session['groups']
        iterate_bio = False

        # 1) admin
        if username in app.config['FACULTY_BIOS_ADMINS']:
            iterate_bio = True

        # 2) user's bio
        if author is not None and username in author:
            iterate_bio = True

        # 3) user is in special group -- check school
        if 'parlau' in groups:
            schools_to_check = ['College of Arts and Sciences']
        elif 'Faculty Approver - CAPS GS' in groups:
            schools_to_check = ['College of Adult and Professional Studies', 'Graduate School']
        elif 'Faculty Approver - Seminary' in groups:
            schools_to_check = ['Bethel Seminary']
        else:
            schools_to_check = None

        if schools_to_check:
            # todo: make this get job-title schools
            school_value = child.find('system-data-structure/job-titles/school')['text']
            if school_value in schools_to_check:
                iterate_bio = True

        # 4) user is in web admin group
        program_elements = []
        program_elements.append(child.find('system-data-structure/job-titles/department'))
        program_elements.append(child.find('system-data-structure/job-titles/seminary-program'))

        if self.check_web_author_groups(groups, program_elements):
            iterate_bio = True

        # get value of bio, if allowed
        if iterate_bio:
            try:
                return self._iterate_child_xml(child, author)
            except AttributeError:
                # Todo: remove this print line, once this is tested
                print 'bad'
                return None
        else:
            return None

    def _iterate_child_xml(self, child, author):

        try:
            workflow_status = child.find('workflow').find('status').text
        except AttributeError:
            workflow_status = None

        if '_shared-content' not in child.find('path').text:
            # get all associated schools
            school_array = []
            for school in child.findall('.//job-titles/school'):
                school_array.append(school.text or 'Other')

            school_array = list(set(school_array))

            page_values = {
                'author': child.find('author') or None,
                'id': child.attrib['id'] or "",
                'title': child.find('title').text or None,
                'created-on': child.find('created-on').text or None,
                'path': 'https://www.bethel.edu' + child.find('path').text or "",
                'schools': school_array,
                'last-name': child.find('.//last').text or None,
                'deactivated': child.find('.//deactivate').text or None
            }
            return page_values
        else:
            return None

    # if the department metadata is found return it, else return ''
    def check_web_author_groups(self, groups, program_elements):
        mapping = {
            'Anthropology, Sociology, & Reconciliation':    'Anthropology Sociology',
            'Art & Design':                                 'Art',
            'Biblical & Theological Studies':               'Biblical Theological',
            'Biological Sciences':                          'Biology',
            'Business & Economics':                         'Business Economics',
            'Chemistry':                                    'Chemistry',
            'Communication Studies':                        'Communication',
            'Education':                                    'Education',
            'English':                                      'English',
            'Environmental Studies':                        'Environmental Studies',
            'General Education':                            'General Education',
            'History':                                      'History',
            'Honors':                                       'Honors',
            'Human Kinetics & Applied Health Science':      'Human Kinetics',
            'Math & Computer Science':                      'Math CS',
            'Modern World Languages':                       'World Languages',
            'Music':                                        'Music',
            'Nursing':                                      'Nursing',
            'Philosophy':                                   'Philosophy',
            'Physics & Engineering':                        'Physics',
            'Political Science':                            'Political Science',
            'Psychology':                                   'Psychology',
            'Social Work':                                  'Social Work',
            'Theatre Arts':                                 'Theatre',
            'Doctor of Ministry':                           'Doctor of Ministry'
        }

        for program_element in program_elements:
            try:
                if mapping[program_element['text']] in groups:
                    return True
            except:
                continue
        return False

    # todo: do what check_job_titles does
    def check_degrees(self, form):
        degrees = {}
        degrees_good = False

        num_degrees = int(form['num_degrees'])

        for x in range(1, num_degrees + 1):  # the page doesn't use 0-based indexing

            i = str(x)
            school_l = 'school' + i
            degree_earned_l = 'degree-earned' + i
            year_l = 'year' + i

            school = form[school_l]
            degree_earned = form[degree_earned_l]
            year = form[year_l]

            degrees[school_l] = school
            degrees[degree_earned_l] = degree_earned
            degrees[year_l] = year

            check = school and degree_earned and year

            if check:
                degrees_good = True

        # convert event dates to JSON
        return json.dumps(degrees), degrees_good, num_degrees

    def check_job_titles(self, form):
        new_jobs_good = False

        num_new_jobs = int(form['num_new_jobs'])

        def safe_get(key, default_return=False, preferred_return=None):
            try:
                to_return = form[key]
                if to_return == 'None' or to_return == '':
                    return False
                if preferred_return is not None:
                    return preferred_return
                return to_return
            except:
                return default_return

        for x in range(1, num_new_jobs + 1):  # the page doesn't use 0-based indexing

            i = str(x)
            school_l = 'schools' + i
            undergrad_l = 'undergrad' + i
            caps_l = 'adult-undergrad' + i
            gs_l = 'graduate' + i
            seminary_l = 'seminary' + i
            dept_chair_l = 'dept-chair' + i
            program_director_l = 'program-director' + i
            lead_faculty_l = 'lead-faculty' + i
            job_title_l = 'new-job-title' + i

            school = safe_get(school_l)
            undergrad = safe_get(undergrad_l, preferred_return=True)
            caps = safe_get(caps_l, preferred_return=True)
            gs = safe_get(gs_l, preferred_return=True)
            seminary = safe_get(seminary_l, preferred_return=True)
            dept_chair = safe_get(dept_chair_l, preferred_return=True)
            program_director = safe_get(program_director_l, preferred_return=True)
            lead_faculty = safe_get(lead_faculty_l, preferred_return=True)
            job_title = safe_get(job_title_l, preferred_return=True)

            check = (school == 'Bethel University' and job_title) or \
                    ((undergrad or caps or gs or seminary) and (dept_chair or program_director or lead_faculty))
            if check:
                new_jobs_good = True

        # convert event dates to JSON
        return new_jobs_good, num_new_jobs

    def update_structure(self, faculty_bio_data, sdata, rform, faculty_bio_id=None):

        wysiwyg_keys = ['biography', 'courses', 'awards', 'publications', 'presentations', 'certificates', 'organizations', 'hobbies']
        add_data = self.get_add_data([], rform, wysiwyg_keys)

        add_data['education'] = self.get_degrees(add_data)
        # todo: these wysiwyg checkboxes aren't returning correctly for the wysiwygs
        add_data['options'] = self.get_wysiwyg_checkboxes(add_data)
        add_data['job-titles'] = self.get_job_titles(add_data)

        add_data['parentFolderID'] = None
        add_data['parentFolderPath'] = '/academics/faculty'
        add_data['path'] = None
        add_data['author'] = session['username']
        faculty_bio_data['page']['metadata']['metaDescription'] = self.build_description(add_data)

        for wysiwyg_key in wysiwyg_keys:
            add_data[wysiwyg_key] = escape_wysiwyg_content(add_data[wysiwyg_key])

        # todo: eventually adjust the keys in cascade to work.
        add_data['started-at-bethel'] = add_data['started_at_bethel']
        add_data['image'] = self.create_faculty_bio_image(add_data)

        workflow_id = self.get_correct_workflow_id(add_data)
        workflow = self.create_workflow(workflow_id, subtitle=add_data['title'])
        self.add_workflow_to_asset(workflow, faculty_bio_data)

        if faculty_bio_id:
            add_data['id'] = faculty_bio_id
        else:
            add_data['id'] = None

        self.update_asset(faculty_bio_data, add_data)

        return faculty_bio_data

    def create_faculty_bio_image(self, add_data):
        from forms import FacultyBioForm
        form = FacultyBioForm()

        # a quick check to quit out if necessary.
        try:
            uploaded_image = form.image.data.filename
        except AttributeError:
            return None

        image_name = add_data['system_name'] + '.jpg'
        image_sub_path = 'academics/faculty/images'
        image_path = image_sub_path + '/' + image_name
        description = self.build_description(add_data)

        # todo: someday change how this is done.
        form.image.data.save(app.config['UPLOAD_FOLDER'] + image_name)
        image_file = open(app.config['UPLOAD_FOLDER'] + image_name, 'r')
        stream = image_file.read()
        encoded_stream = base64.b64encode(stream)

        file_asset = self.read(image_path, 'file')
        # edit existing
        if file_asset['success'] == 'true':
            image_asset = file_asset['asset']['file']
            # update data
            new_values = {
                'data': encoded_stream,
                'metaDescription': description,
            }

            self.update_asset(image_asset, new_values)
            resp = self.cascade_connector.create(image_asset)
            clear_resp = self.clear_image_cache(image_path)
            self.log_sentry('Editted Faculty Bio Image', resp)

        # create new from base_asset
        else:
            try:
                image_asset = self.read(app.config['IMAGE_WITH_DEFAULT_IMAGE_BASE_ASSET'], 'file')['asset']
            except:
                return None

            new_values = {
                'createdBy': 'tinker',
                'createdDate': None,
                'data': encoded_stream,
                'id': None,
                'metaDescription': description,
                'name': image_name,
                'path': None,
                'parentFolderId': None,
                'parentFolderPath': image_sub_path
            }

            self.update_asset(image_asset, new_values)
            resp = self.cascade_connector.create(image_asset)
            self.log_sentry('Created Faculty Bio Image', resp)

        self.publish(image_path, 'file')
        return image_path

    # this can be shortened, i hope
    def build_description(self, add_data):
        description = "Meet " + add_data['first'] + " " + add_data['last']

        # recurse through all job titles
        schools_found = []
        for i in range(1, 100):
            # new_job_title = None

            try:
                schools_found.append(add_data['schools' + str(i)])
            except:
                break

            if 'program-director' + str(i) in add_data and add_data['program-director' + str(i)] == 'Yes':
                new_job_title = 'Program Director'
            elif 'dept-chair' + str(i) in add_data and add_data['dept-chair' + str(i)] == 'Yes':
                new_job_title = 'Department Chair'
            elif 'lead-faculty' + str(i) in add_data and add_data['lead-faculty' + str(i)] != 'Other' and add_data[
                        'lead-faculty' + str(i)] is not None:
                new_job_title = add_data['lead-faculty' + str(i)]
            elif 'new-job-title' + str(i) in add_data:
                new_job_title = add_data['new-job-title' + str(i)].strip()
            else:
                break

            punctuation = ', '
            if i == 2 and 'schools3' not in add_data:
                punctuation = ' and '
            elif i >= 3 and 'schools' + str(i + 1) not in add_data:
                punctuation = ', and '
            description += punctuation + new_job_title

        # check if they are in only seminary
        in_sem = 'Bethel Seminary' in schools_found
        not_in_bu = 'Bethel University' not in schools_found
        not_in_cas = 'College of Arts and Sciences' not in schools_found
        not_in_caps = 'College of Adult and Professional Studies' not in schools_found
        not_in_gs = 'Graduate School' not in schools_found

        if in_sem and not_in_bu and not_in_cas and not_in_caps and not_in_gs:
            description += ', at Bethel Seminary.'
        else:
            description += ', at Bethel University.'

        return description

    def get_correct_workflow_id(self, add_data):
        schools = []
        for key in add_data:
            if key.startswith('schools'):
                schools.append(add_data[key])
        if "College of Arts and Sciences" in schools:
            return 'f1638f598c58651313b6fe6b5ed835c5'
        elif "Graduate School" in schools or "College of Adult and Professional Studies" in schools:
            return '81dabbc78c5865130c130b3a2b567e75'
        elif "Bethel Seminary" in schools:
            return '68ad793e8c5865137c9c2c89440cbbbc'

    def should_be_able_to_edit_image(self, roles):
        if 'FACULTY-CAS' in roles or 'FACULTY-BSSP' in roles or 'FACULTY-BSSD' in roles:
            return False
        else:
            return True

    def validate_form(self, rform):
        from forms import FacultyBioForm
        form = FacultyBioForm()

        degrees, degrees_good, num_degrees = self.check_degrees(rform)
        new_jobs_good, num_new_jobs = self.check_job_titles(rform)
        if not form.validate_on_submit() or (not new_jobs_good or not degrees_good):
            if 'faculty_bio_id' in request.form.keys():
                faculty_bio_id = request.form['faculty_bio_id']
            else:
                # This error came from the add form because event_id wasn't set
                add_form = True

            metadata = fjson.dumps(data_to_add)
            return render_template('faculty-bio-form.html', **locals())

    def get_degrees(self, add_data):
        degrees = []

        # format the dates
        for i in range(1, 200):
            i = str(i)
            try:
                school = add_data['school' + i]
                degree = add_data['degree-earned' + i]
                year = add_data['year' + i]
            except KeyError:
                # This will break once we run out of degrees
                break

            education = {
                'school': school,
                'degree-earned': degree,
                'year': year
            }

            degrees.append(education)

        return degrees

    def get_job_titles(self, add_data):
        job_titles = []

        # format the dates
        for i in range(1, 200):
            i = str(i)
            # todo: update this try/except block
            try:
                # currently this is just making sure a school exists, if it doesn't break out.
                schools = add_data['schools' + i]
            except KeyError:
                # This will break once we run out of new job titles
                break

            full_job_title = {
                'school': add_data.get('schools' + i, ''),
                'department': add_data.get('undergrad' + i, 'None'),
                'adult-undergrad-program': add_data.get('adult-undergrad' + i, 'None'),
                'graduate-program': add_data.get('graduate' + i, 'None'),
                'seminary': add_data.get('seminary' + i, 'None'),
                'department-chair': add_data.get('dept-chair' + i, 'No'),
                'program-director': add_data.get('program-director' + i, 'No'),
                'lead-faculty': add_data.get('lead-faculty' + i, 'Other'),
                'job_title': add_data.get('new-job-title' + i, '')
            }

            job_titles.append(full_job_title)

        return job_titles

    # this is used to generate the checkboxes that aren't on the tinker form, but are on the Cascade DataDef
    def get_wysiwyg_checkboxes(self, add_data):

        options = []

        if add_data.get('biography', '') != "":
            options.append("::CONTENT-XML-CHECKBOX::Biography")
        if add_data.get('awards', '') != "":
            options.append("::CONTENT-XML-CHECKBOX::Awards")
        if add_data.get('courses', '') != "":
            options.append("::CONTENT-XML-CHECKBOX::Courses Taught")
        if add_data.get('publications', '') != "":
            options.append("::CONTENT-XML-CHECKBOX::Publications")
        if add_data.get('presentations', '') != "":
            options.append("::CONTENT-XML-CHECKBOX::Presentations")
        if add_data.get('certificates', '') != "":
            options.append("::CONTENT-XML-CHECKBOX::Certificates and Licenses")
        if add_data.get('courses', '') != "":
            options.append("::CONTENT-XML-CHECKBOX::Professional Organizations, Committees, and Boards")
        if add_data.get('hobbies', '') != "":
            options.append("::CONTENT-XML-CHECKBOX::Hobbies and Interests")
        if add_data.get('quote', '') != "":
            options.append("::CONTENT-XML-CHECKBOX::Quote")
        if add_data.get('website', '') != "":
            options.append("::CONTENT-XML-CHECKBOX::Website")

        return ''.join(options)

    # this callback is used with the /edit_all endpoint. The primary use is to modify all assets
    def edit_all_callback(self, asset_data):
        pass

# Global
import base64
import json
import re
import os
import platform

# Packages
from bu_cascade.asset_tools import find
from flask import session

# Local
from tinker import app
from tinker.tinker_controller import TinkerController
from unidecode import unidecode


class FacultyBioController(TinkerController):
    def get_mapping(self):
        mapping = {
            'Anthropology, Sociology, & Reconciliation':    'Anthropology Sociology',
            'Art & Design':                                 'Art',
            'Biblical & Theological Studies':               'Biblical Theological',
            'Biological Sciences':                          'Biology',
            'Business & Economics':                         'Business Economics',
            'Chemistry':                                    'Chemistry',
            'Communication Studies':                        'Communication',
            'Doctor of Ministry':                           'Doctor of Ministry',
            'Education':                                    'Education',
            'English':                                      'English',
            'Environmental Studies':                        'Environmental Studies',
            'General Education':                            'General Education',
            'History':                                      'History',
            'Honors':                                       'Honors',
            'Human Kinetics & Applied Health Science':      'Human Kinetics',
            'Math & Computer Science':                      'Math CS',
            'Music':                                        'Music',
            'Nursing':                                      'Nursing',
            'Philosophy':                                   'Philosophy',
            'Physics & Engineering':                        'Physics',
            'Political Science':                            'Political Science',
            'Psychology':                                   'Psychology',
            'Social Work':                                  'Social Work',
            'Theatre Arts':                                 'Theatre',
            'World Languages and Cultures':                 'World Languages',
        }
        return mapping

    def inspect_child(self, child, find_all=False, csv=False):
        # Set up the variables that this method will use to determine whether or not it should iterate over this bio
        author = None
        try:
            author = child.find('author').text.replace(' ', '').split(',')
        except AttributeError:
            pass

        username = session['username']
        groups = session['groups']
        program_elements = [
            child.findall('system-data-structure/job-titles/department'),
            child.findall('system-data-structure/job-titles/seminary-program')
        ]
        iterate_bio = False

        # Go through the 5 conditions when we would want to iterate over the fac bio, 'child', and chain them into an
        # if/elif chain so that as soon as we have a successful condition, it doesn't need to check the other
        # conditions. Following that line of thought, they've been organized from fastest check to slowest check to get
        # a successful condition as fast as possible, and then move on.
        if find_all:
            # Because we're iterating over all of the bios.
            iterate_bio = True
        elif 'Tinker Faculty Bios - Admin' in groups or 'Administrators' in groups:
            # Because the user running this operation is an administrator
            iterate_bio = True
        elif author is not None and username in author:
            # Because the user running this operation is one of the people who created/edited this bio
            iterate_bio = True
        elif self.check_web_author_groups(groups, program_elements):
            # Because the user running this operation is in a group that's authorized to edit this bio
            iterate_bio = True
        else:
            if 'Tinker Faculty Bios - CAS' in groups:
                schools_to_check = ['College of Arts and Sciences']
            elif 'Tinker Faculty Bios - CAPS and GS' in groups:
                schools_to_check = ['College of Adult and Professional Studies', 'Graduate School']
            elif 'Tinker Faculty Bios - SEM' in groups:
                schools_to_check = ['Bethel Seminary']
            else:
                schools_to_check = []

            if len(schools_to_check) > 0:
                school_values = []
                try:
                    school_values = [school.text for school in child.findall('system-data-structure/job-titles/school')]
                except:
                    pass

                for school_value in school_values:
                    if school_value in schools_to_check:
                        # Because the user running this operation is in a group allowed to edit all bios for this bio's
                        # particular school
                        iterate_bio = True
                        # Don't need to keep iterating through school values in the bio if we already have a match
                        break

        to_return = None
        if iterate_bio:
            try:
                to_return = self._iterate_child_xml(child, author, csv)
            except AttributeError:
                pass

        return to_return

    def _iterate_child_xml(self, child, author, csv=False):

        try:
            workflow_status = child.find('workflow').find('status').text
        except AttributeError:
            workflow_status = None

        if '_shared-content' not in child.find('path').text:
            # get all associated schools
            school_array = []
            for school in child.findall('.//job-titles/school'):
                school_array.append(school.text or 'Other')
            if csv:
                return self.csv_file(child)
            else:
                page_values = {
                    'author': child.find('author') or None,
                    'id': child.attrib['id'] or "",
                    'title': child.find('title').text or None,
                    'created-on': child.find('created-on').text or None,
                    'path': 'https://www.bethel.edu' + child.find('path').text or "",
                    'schools': school_array,
                    'last-name': child.find('.//last').text or None,
                    'deactivated': child.find('.//deactivate').text or None,
                    'courseleaf-user': child.find('.//courseleaf-user').text or "Yes"
                }

            # Returns the page_values
            return page_values
        else:
            return None

    def csv_file(self, child):
        # Initial dictionary values
        page_values = {
            'first': self.get_faculty_data(child, 'first'),
            'last': self.get_faculty_data(child, 'last'),
            'highlight': self.get_faculty_data(child, 'highlight'),
            'email': self.get_faculty_data(child, 'email'),
            'started-at-bethel': self.get_faculty_data(child, 'started-at-bethel'),
            'location': '',
            'biography': self.wysiwyg_inner_text(child, 'add-to-bio/biography'),
            'courses': self.wysiwyg_inner_text(child, 'add-to-bio/courses'),
            'awards': self.wysiwyg_inner_text(child, 'add-to-bio/awards'),
            'publications': self.wysiwyg_inner_text(child, 'add-to-bio/publications'),
            'presentations': self.wysiwyg_inner_text(child, 'add-to-bio/presentations'),
            'certificates': self.wysiwyg_inner_text(child, 'add-to-bio/certificates'),
            'organizations': self.wysiwyg_inner_text(child, 'add-to-bio/organizations'),
            'hobbies': self.wysiwyg_inner_text(child, 'add-to-bio/hobbies'),
            'research-interests': self.get_faculty_data(child, 'add-to-bio/research-interests'),
            'areas': self.get_faculty_data(child, 'add-to-bio/areas'),
            'teaching-specialty': self.get_faculty_data(child, 'add-to-bio/teaching-specialty'),
            'quote': self.get_faculty_data(child, 'add-to-bio/quote'),
            'website': self.get_faculty_data(child, 'add-to-bio/website')
        }

        # Checks to make sure there is an author if not sets author to an empty string
        if str(child.find('author')) == 'None':
            page_values['author'] = ""
        else:
            page_values['author'] = child.find('author').text

        # Checks to see if there are multiple values for the faculty location field
        if str(child.find('.//faculty_location/value')) != 'None':
            location = ""
            for values in child.findall('.//faculty_location/value'):
                location += values.text + '\n'
            page_values['location'] = location.rstrip()

        # Iterates through all the job fields and adds it to the dictionary on the fly
        max_jobs = 0
        for jobs in child.findall('.//job-titles'):
            max_jobs += 1
            school = self.get_faculty_data(jobs, 'school')
            page_values['school' + str(max_jobs)] = school
            page_values['job_title' + str(max_jobs)] = self.get_faculty_data(jobs, 'job_title')
            page_values['department' + str(max_jobs)] = ""
            if school == 'College of Arts and Sciences':
                page_values['department' + str(max_jobs)] = self.get_faculty_data(jobs, 'department')
                if self.get_faculty_data(jobs, 'department-chair') == 'Yes':
                    page_values['job_title' + str(max_jobs)] = 'Department Chair'
            elif school == 'College of Adult and Professional Studies':
                page_values['department' + str(max_jobs)] = self.get_faculty_data(jobs, 'adult-undergrad-program')
                if self.get_faculty_data(jobs, 'program-director') == 'Yes':
                    page_values['job_title' + str(max_jobs)] = 'Program Director'
            elif school == 'Graduate School':
                page_values['department' + str(max_jobs)] = self.get_faculty_data(jobs, 'graduate-program')
                if self.get_faculty_data(jobs, 'program-director') == 'Yes':
                    page_values['job_title' + str(max_jobs)] = 'Program Director'
            elif school == 'Bethel Seminary':
                page_values['department' + str(max_jobs)] = self.get_faculty_data(jobs, 'seminary-program')
                if self.get_faculty_data(jobs, 'program-director') == "Yes":
                    page_values['job_title' + str(max_jobs)] = 'Program Director'
                elif self.get_faculty_data(jobs, 'lead-faculty') != "Other":
                    page_values['job_title' + str(max_jobs)] = jobs.find('lead-faculty').text

        page_values['max-jobs'] = max_jobs

        # Iterates through all the education fields and adds it to the dictionary on the fly
        max_edu = 0
        for edu in child.findall('.//education'):
            max_edu += 1
            page_values['school-edu' + str(max_edu)] = unidecode(self.get_faculty_data(edu, 'school'))
            page_values['degree-earned' + str(max_edu)] = self.get_faculty_data(edu, 'degree-earned')
            page_values['year' + str(max_edu)] = self.get_faculty_data(edu, 'year')

        page_values['max-edu'] = max_edu

        # return the dictionary
        return page_values

    # TODO: Remove version checking (and wysiwyg_inner_text_rec method) when upgrading to python 2.7
    # A method used to extract all the inner text from the wysiwyg's
    def wysiwyg_inner_text(self, child, path_tail):
        if platform.python_version()[:3] == '2.6':
            data = child.find('.//' + str(path_tail)).getchildren()
            return self.wysiwyg_inner_text_rec(data)
        else:
            string = ""
            for information in child.find('.//' + str(path_tail)).itertext():
                string += information
                # strings the newline character from the end of the new string (including the new information)
                string = string.rstrip()
                # Adds a newline character so that the string isn't just a continuing line of text without spaces
                # between new information
                string += '\n'
            # strips the newline character from before any of the information
            string = string.lstrip()
            # strips the string again so that there isn't any white lines between information
            return string.rstrip()

    def wysiwyg_inner_text_rec(self, data):
        string = ''
        for things in data:
            if things.text is None:
                things_text = ''
            else:
                things_text = things.text.rstrip()
            if things.tail is None:
                things_tail = ''
            else:
                things_tail = things.tail
            if things.getchildren() is None:
                things_children = ''
            else:
                things_children = self.wysiwyg_inner_text_rec(things.getchildren())
            string += things_text + things_children + things_tail.rstrip()
            string = string.rstrip()
            if things.tag != 'strong' and things.tag != 'em':
                string += '\n'
        return string.rstrip()

    # A method used to check if the field is empty or not, if empty returns empty string, else returns the data.
    def get_faculty_data(self, child, path_tail):
        string = child.find('.//' + str(path_tail)).text
        if string is None:
            return ''
        else:
            return string

    # if the department metadata is found return it, else return ''
    def check_web_author_groups(self, groups, program_elements):
        # todo: this mapping should somehow be automatic with the program name changes! Currently, if a program
        # name is changed in the metadata, the faculty bios won't be synced up with the cascade group

        for program_element in program_elements:
            for program in program_element:
                try:
                    if self.get_mapping()[program.text] in groups.split(';'):
                        return True
                except:
                    continue
        return False

    def is_user_in_web_author_groups(self):
        for key, value in self.get_mapping().iteritems():
            # TODO: PG, Aug 9 2017: I removed a try/except block from around this if statement since it appears useless
            # If there are exceptions all of a sudden, this is how to fix it.
            if value in session['groups']:
                return True

        return False

    # todo: do what check_job_titles does
    def check_degrees(self, form):
        degrees = {}
        failed_check = False
        error_list = []

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

            if not check:
                error_list.append(u'Degree #' + i + u' has an error')
                failed_check = True
        # convert event dates to JSON
        return json.dumps(degrees), not failed_check, error_list, num_degrees

    def check_job_titles(self, form):
        failed_check = False
        error_list = []

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
            dept_chair, d_c_value = safe_get(dept_chair_l, preferred_return=True), safe_get(dept_chair_l)
            program_director, p_d_value = safe_get(program_director_l, preferred_return=True), safe_get(program_director_l)
            lead_faculty, l_f_value = safe_get(lead_faculty_l, preferred_return=True), safe_get(lead_faculty_l)
            job_title = safe_get(job_title_l, preferred_return=True)

            if school == "-select-":
                error_list.append(u'You must select a school for Job Title #' + i)
                failed_check = True

            staff_check = (school == 'Bethel University' and job_title)
            cas_check = (school == 'College of Arts and Sciences' and undergrad and dept_chair and
                         ((d_c_value == 'Yes') or (d_c_value == 'No' and job_title)))
            caps_check = (school == 'College of Adult and Professional Studies' and caps and program_director and
                          ((p_d_value == 'Yes') or (p_d_value == 'No' and job_title)))
            gs_check = (school == 'Graduate School' and gs and program_director and
                        ((p_d_value == 'Yes') or (p_d_value == 'No' and job_title)))
            sem_check = (school == 'Bethel Seminary' and seminary and lead_faculty and
                         (((l_f_value == 'Lead Faculty' or l_f_value == 'Program Director')) or
                          (l_f_value == 'Other' and job_title)))

            check = staff_check or cas_check or caps_check or gs_check or sem_check
            # check = (school == 'Bethel University' and job_title) or \
            # ((undergrad or caps or gs or seminary) and (dept_chair or program_director or lead_faculty or job_title))
            if not check:
                error_list.append(u'Job Title #' + i + u' has an error')
                failed_check = True

        return not failed_check, error_list, num_new_jobs

    def update_structure(self, faculty_bio_data, sdata, rform, faculty_bio_id=None, submitter_groups=''):
        add_data = self.get_add_data(['faculty_location'], rform)

        add_data['last'] = add_data['last'].strip()
        add_data['first'] = add_data['first'].strip()

        add_data['education'] = self.get_degrees(add_data)
        # todo: these wysiwyg checkboxes aren't returning correctly for the wysiwygs
        add_data['options'] = self.get_wysiwyg_checkboxes(add_data)
        add_data['job-titles'] = self.get_job_titles(add_data)
        # this is joining a list of locations and prepending the '::CONTENT-XML-SELECTOR::' to each location
        add_data['faculty_location'] = ''.join(['::CONTENT-XML-SELECTOR::' + location for location in add_data['faculty_location']])

        # set/reset the standard data
        add_data['parentFolderID'] = None
        if not app.config['UNIT_TESTING']:
            add_data['parentFolderPath'] = '/academics/faculty'
        else:
            add_data['parentFolderPath'] = '/_testing/philip-gibbens/fac-bios-tests'
        add_data['path'] = None
        faculty_bio_data['page']['metadata']['metaDescription'] = self.build_description(add_data)

        # todo: eventually adjust the keys in cascade to work.
        add_data['author'] = add_data['author_faculty']

        # todo: eventually adjust the keys in cascade to work.
        add_data['started-at-bethel'] = add_data['started_at_bethel']
        add_data['teaching-specialty'] = add_data['teaching_specialty']
        add_data['research-interests'] = add_data['research_interests']
        try:
            add_data['courseleaf-user'] = add_data['courseleaf_user']
        except KeyError:
            pass

        # todo: this is a temp fix to override the already set system-name
        new_system_name = add_data['last'].strip() + '-' + add_data['first'].strip()
        new_system_name = new_system_name.lower().replace(' ', '-')
        add_data['system_name'] = re.sub(r'[^a-zA-Z0-9-]', '', new_system_name)

        # this needs to be done AFTER the system name is made.
        add_data['image'] = self.create_faculty_bio_image(add_data)

        workflow_id = self.get_correct_workflow_id(add_data, submitter_groups)
        workflow = self.create_workflow(workflow_id, subtitle=add_data['title'])
        self.add_workflow_to_asset(workflow, faculty_bio_data)

        if faculty_bio_id:
            add_data['id'] = faculty_bio_id
        else:
            add_data['id'] = None

        # Today's Date: (08/09/18)
        # This hacky chunk of code is used to add the "courseleaf-user" value to the faculty_bio_data. The value
        # currently doesn't exist for most faculty bios since "courseleaf-user" was recently added to the faculty bio
        # xml.
        # Thus since the "courseleaf-user" value doesn't currently exist in the faculty_bio_data we either would have to
        # edit and submit every faculty bio in Cascade (taking hours to do so) or do this. This code adds a default
        # value of "Yes" to every faculty bio whose faculty_bio_data currently does not have the "courseleaf-user" key
        # in the dictionary. This data then is added to the asset when update_asset is called on line ~451.
        if not find(faculty_bio_data, 'courseleaf-user', False):
            faculty_bio_data.get('page').get('structuredData').get('structuredDataNodes').get(
                'structuredDataNode').append({'text': 'Yes', 'identifier': 'courseleaf-user', 'type': 'text'})

        self.update_asset(faculty_bio_data, add_data)

        return faculty_bio_data

    def create_faculty_bio_image(self, add_data):
        from forms import FacultyBioForm
        form = FacultyBioForm()

        self.log_sentry('Faculty Bio Image: Form', form)
        # todo: add in sentry error for submission (include form.image.data.filename)
        try:
            # an image was uploaded
            form.image.data.filename

        except AttributeError:
            # no image selected - make sure to keep the image url as is.
            return add_data.get('image_url')

        image_name = add_data['system_name'] + '.jpg'
        image_sub_path = '/academics/faculty/images'
        image_path = image_sub_path + '/' + image_name
        description = self.build_description(add_data)
        self.log_sentry('Faculty Bio Image: Name', image_name)

        form.image.data.save(app.config['UPLOAD_FOLDER'] + image_name)

        image_file = open(app.config['UPLOAD_FOLDER'] + image_name, 'r')

        # the image is 0 bytes
        if os.fstat(image_file.fileno()).st_size <= 0:
            return add_data.get('image_url')
        else:
            stream = image_file.read()
            encoded_stream = base64.b64encode(stream)

            file_asset = self.read(image_path, 'file')

            # edit existing
            if file_asset['success'] == 'true':
                image_asset = file_asset['asset']
                # update data
                new_values = {
                    'data': encoded_stream,
                    'metaDescription': description,
                }

                self.update_asset(image_asset, new_values)
                resp = self.cascade_connector.edit(image_asset)
                clear_resp = self.clear_image_cache(image_path)
                self.log_sentry('Edited Faculty Bio Image', resp)

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

            # delete the old image, if their name is changed (since it would have created a new image anyway.
            if add_data.get('image_url') and add_data.get('image_url') != image_path:
                self.delete(add_data.get('image_url'), 'file')

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

    def get_correct_workflow_id(self, add_data, groups):
        # Check if the person making the edit is one of the designated FacBio approvers
        # If they are, send the edit to their workflow so that they can always approve their own edits.
        # Groups is a String of semicolon-separated Cascade Group names
        if 'Faculty Approver - CAS' in groups:
            return app.config['FACULTY_BIOS_WORKFLOW_CAS_ID']
        elif 'Faculty Approver - CAPS GS' in groups:
            return app.config['FACULTY_BIOS_WORKFLOW_CAPSGS_ID']
        elif 'Faculty Approver - Seminary' in groups:
            return app.config['FACULTY_BIOS_WORKFLOW_SEM_ID']
        else:
            # If the submitter isn't one of the approvers, use the normal logic to assign a workflow
            schools = []
            for key in add_data:
                if key.startswith('schools'):
                    schools.append(add_data[key])
            if 'College of Arts and Sciences' in schools:
                return app.config['FACULTY_BIOS_WORKFLOW_CAS_ID']
            elif 'Graduate School' in schools or 'College of Adult and Professional Studies' in schools:
                return app.config['FACULTY_BIOS_WORKFLOW_CAPSGS_ID']
            elif 'Bethel Seminary' in schools:
                return app.config['FACULTY_BIOS_WORKFLOW_SEM_ID']
            else:
                return app.config['FACULTY_BIOS_WORKFLOW_CAS_ID']

    def should_be_able_to_edit_image(self):
        roles = set(session['roles'])
        wanted_roles = set(['FACULTY-CAPS', 'RECENT-FACULTY-CAPS', 'FACULTY-GS', 'RECENT-FACULTY-GS'])
        has_roles = wanted_roles.intersection(roles)

        groups = set(session['groups'].split(';'))
        wanted_groups = set(['Tinker Faculty Bios'])
        has_groups = wanted_groups.intersection(groups)

        return bool(has_roles or has_groups)

    def validate_form(self, rform):
        from forms import FacultyBioForm
        form = FacultyBioForm(rform)

        # todo: remove this code for jenny vang soon
        # this allows jenny vang to submit any faculty bio form even if it has errors
        if session['username'] == 'jev24849':
            return form

        degrees, degrees_good, degree_error_list, num_degrees = self.check_degrees(rform)
        new_jobs_good, new_jobs_error_list, num_new_jobs = self.check_job_titles(rform)
        if not (form.validate() and new_jobs_good and degrees_good):
            if not new_jobs_good:
                for error in new_jobs_error_list:
                    form.new_job_titles.errors.append(error)
                form.errors['new_job_titles'] = new_jobs_error_list
            if not degrees_good:
                for error in degree_error_list:
                    form.degree.errors.append(error)
                form.errors['degree'] = degree_error_list
        return form

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
                'seminary-program': add_data.get('seminary' + i, 'None'),
                'department-chair': add_data.get('dept-chair' + i, 'No'),
                'program-director': add_data.get('program-director' + i, 'No'),
                'lead-faculty': add_data.get('lead-faculty' + i, 'Other'),
                'job_title': add_data.get('new-job-title' + i, '')
            }

            job_titles.append(full_job_title)

        return job_titles

    # this is used to generate the checkboxes that aren't on the tinker form, but are on the Cascade DataDef
    def get_wysiwyg_checkboxes(self, add_data):
        # TODO: this checks for 'courses' twice and assigns a different value each time, should be investigated
        options = []

        if add_data.get('biography', None):
            options.append("::CONTENT-XML-CHECKBOX::Biography")
        if add_data.get('awards', None):
            options.append("::CONTENT-XML-CHECKBOX::Awards")
        if add_data.get('courses', None):
            options.append("::CONTENT-XML-CHECKBOX::Courses Taught")
        if add_data.get('publications', None):
            options.append("::CONTENT-XML-CHECKBOX::Publications")
        if add_data.get('presentations', None):
            options.append("::CONTENT-XML-CHECKBOX::Presentations")
        if add_data.get('certificates', None):
            options.append("::CONTENT-XML-CHECKBOX::Certificates and Licenses")
        if add_data.get('courses', None):
            options.append("::CONTENT-XML-CHECKBOX::Professional Organizations, Committees, and Boards")
        if add_data.get('hobbies', None):
            options.append("::CONTENT-XML-CHECKBOX::Hobbies and Interests")
        if add_data.get('areas', None):
            options.append("::CONTENT-XML-CHECKBOX::Areas of expertise")
        if add_data.get('research_interests', None):
            options.append("::CONTENT-XML-CHECKBOX::Research interests")
        if add_data.get('teaching_specialty', None):
            options.append("::CONTENT-XML-CHECKBOX::Teaching specialty")
        if add_data.get('quote', None):
            options.append("::CONTENT-XML-CHECKBOX::Quote")
        if add_data.get('website', None):
            options.append("::CONTENT-XML-CHECKBOX::Website")

        return ''.join(options)

    # this callback is used with the /edit_all endpoint. The primary use is to modify all assets
    def edit_all_callback(self, asset_data):
        # first_name = find(asset_data, 'first', False)
        # last_name = find(asset_data, 'last', False)
        # update(asset_data, 'name', last_name.lower() + '-' + first_name.lower())
        # update(asset_data, 'title', first_name + ' ' + last_name)

        # Todo: remove this code when the faculty bios have been successfully been transferred.
        # # move areas of interest
        # expertise = find(asset_data, 'expertise', False)
        # heading = find(expertise, 'heading', False)
        # new_highlight_value = ''
        # options_text = find(asset_data, 'options')
        # if 'text' not in options_text:
        #     update(asset_data, 'options', '')
        # options_text = find(asset_data, 'options')['text']
        # if heading == 'Areas of expertise':
        #     new_highlight_value = find(expertise, 'areas', False)
        #     options_text = options_text + '::CONTENT-XML-CHECKBOX::' + 'Areas of expertise'
        #     if find(find(asset_data, 'add-to-bio', False), 'areas') is None:
        #         find(asset_data, 'add-to-bio', False).append({'identifier': 'areas', 'type': 'text', 'text': new_highlight_value})
        #     else:
        #         update(find(asset_data, 'add-to-bio', False), 'areas', new_highlight_value)
        # elif heading == 'Research interests':
        #     new_highlight_value = find(expertise, 'research-interests', False)
        #     options_text = options_text + '::CONTENT-XML-CHECKBOX::' + 'Research interests'
        #     if find(find(asset_data, 'add-to-bio', False), 'research-interests') is None:
        #         find(asset_data, 'add-to-bio', False).append({'identifier': 'research-interests', 'type': 'text', 'text': new_highlight_value})
        #     else:
        #         update(find(asset_data, 'add-to-bio', False), 'research-interests', new_highlight_value)
        # elif heading == 'Teaching Specialty':
        #     new_highlight_value = find(expertise, 'teaching-specialty', False)
        #     options_text = options_text + '::CONTENT-XML-CHECKBOX::' + 'Teaching specialty'
        #     if find(find(asset_data, 'add-to-bio', False), 'teaching-specialty') is None:
        #         find(asset_data, 'add-to-bio', False).append({'identifier': 'teaching-specialty', 'type': 'text', 'text': new_highlight_value})
        #     else:
        #         update(find(asset_data, 'add-to-bio', False), 'teaching-specialty', new_highlight_value)
        #
        # update(asset_data, 'options', options_text)
        #
        # # set highlight text
        # if find(asset_data, 'highlight') is None:
        #     find(asset_data, 'structuredDataNode', False).append({'identifier': 'highlight', 'type': 'text', 'text': new_highlight_value})
        # else:
        #     update(asset_data, 'highlight', new_highlight_value)
        #
        # # set default location to be St. Paul
        # current_location = find(asset_data, 'faculty_location', False)
        # if current_location is None:
        #     find(asset_data, 'structuredDataNode', False).append(
        #         {'identifier': 'faculty_location', 'type': 'text', 'text': ['St. Paul']})

        pass

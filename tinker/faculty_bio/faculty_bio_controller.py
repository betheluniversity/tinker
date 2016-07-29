import json
import re
import urllib2

from operator import itemgetter
from tinker.cascade_tools import *
from tinker.tinker_controller import Cascade
from tinker.tools import *
from tinker.web_services import *
from xml.etree import ElementTree
from tinker.tinker_controller import TinkerController


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
        if username in app.config['FACULTY_BIO_ADMINS']:
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

    # todo: this method is pretty nasty. should refactor (maybe loop over each key to simplify?)
    def check_job_titles(self, form):
        new_jobs_good = False

        num_new_jobs = int(form['num_new_jobs'])

        def safe_get(key, default_return=False, preferred_return=None):
            try:
                to_return = form[key]
                print key + ":", to_return
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

    # todo: delete
    def get_expertise(self, add_data):
        heading = add_data['heading']
        areas = add_data['areas']
        interests = add_data['research_interests']
        teaching = add_data['teaching_specialty']

        data_list = [
            structured_data_node("heading", heading),
            structured_data_node("areas", areas),
            structured_data_node("research-interests", interests),
            structured_data_node("teaching-specialty", teaching),
        ]

        node = {
            'type': "group",
            'identifier': "expertise",
            'structuredDataNodes': {
                'structuredDataNode': data_list,
            },
        }
        return node

    def get_job_titles(self, add_data):
        job_titles = []

        for key in add_data:
            if key.startswith('job-title'):
                job_title = add_data[key]
                job_titles.append(structured_data_node("job-title", job_title))

        return job_titles

    # todo: can be deleted, i think
    def get_new_job_titles(self, add_data):
        new_job_titles = []

        # format the dates
        for key in add_data:
            if key.startswith('schools'):
                schools = add_data[key]
                i = key.split('schools')[1]
            else:
                continue

            undergrad = None
            adult_undergrad = None
            graduate = None
            seminary = None

            dept_chair = None
            program_director = None
            lead_faculty = None
            new_job_title = None

            if 'undergrad' + i in add_data:
                undergrad = add_data['undergrad' + i]
            if 'adult-undergrad' + i in add_data:
                adult_undergrad = add_data['adult-undergrad' + i]
            if 'graduate' + i in add_data:
                graduate = add_data['graduate' + i]
            if 'seminary' + i in add_data:
                seminary = add_data['seminary' + i]

            if 'dept-chair' + i in add_data:
                dept_chair = add_data['dept-chair' + i]
            if 'program-director' + i in add_data:
                program_director = add_data['program-director' + i]
            if 'lead-faculty' + i in add_data:
                lead_faculty = add_data['lead-faculty' + i]
            if 'new-job-title' + i in add_data:
                new_job_title = add_data['new-job-title' + i]

            data_list = [
                structured_data_node("school", schools),
                structured_data_node("department", undergrad),
                structured_data_node("adult-undergrad-program", adult_undergrad),
                structured_data_node("graduate-program", graduate),
                structured_data_node("seminary-program", seminary),

                structured_data_node("department-chair", dept_chair),
                structured_data_node("program-director", program_director),
                structured_data_node("lead-faculty", lead_faculty),

                structured_data_node("job_title", new_job_title),
            ]

            node = {
                'type': "group",
                'identifier': "job-titles",
                'structuredDataNodes': {
                    'structuredDataNode': data_list,
                },
            }

            new_job_titles.append(node)

        return new_job_titles

    # todo: can be deleted, i think
    def get_add_a_degree(self, add_data):
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

            data_list = [
                structured_data_node("school", school),
                structured_data_node("degree-earned", degree),
                structured_data_node("year", year),
            ]

            node = {
                'type': "group",
                'identifier': "add-degree",
                'structuredDataNodes': {
                    'structuredDataNode': data_list,
                },
            }

            degrees.append(node)

        final_node = {
            'type': "group",
            'identifier': "education",
            'structuredDataNodes': {
                'structuredDataNode': degrees,
            },
        }

        return final_node

    # todo: can be deleted, i think
    def get_add_to_bio(self, add_data):
        options = []

        biography = ""
        awards = ""
        courses = ""
        publications = ""
        presentations = ""
        certificates = ""
        organizations = ""
        hobbies = ""
        quote = ""
        website = ""

        if 'biography' in add_data.keys():
            biography = add_data['biography']
        if 'awards' in add_data.keys():
            awards = add_data['awards']
        if 'courses' in add_data.keys():
            courses = add_data['courses']
        if 'publications' in add_data.keys():
            publications = add_data['publications']
        if 'presentations' in add_data.keys():
            presentations = add_data['presentations']
        if 'certificates' in add_data.keys():
            certificates = add_data['certificates']
        if 'organizations' in add_data.keys():
            organizations = add_data['organizations']
        if 'hobbies' in add_data.keys():
            hobbies = add_data['hobbies']
        if 'quote' in add_data.keys():
            quote = add_data['quote']
        if 'website' in add_data.keys():
            website = add_data['website']

        if biography != "":
            options.append("::CONTENT-XML-CHECKBOX::Biography")
        if awards != "":
            options.append("::CONTENT-XML-CHECKBOX::Awards")
        if courses != "":
            options.append("::CONTENT-XML-CHECKBOX::Courses Taught")
        if publications != "":
            options.append("::CONTENT-XML-CHECKBOX::Publications")
        if presentations != "":
            options.append("::CONTENT-XML-CHECKBOX::Presentations")
        if certificates != "":
            options.append("::CONTENT-XML-CHECKBOX::Certificates and Licenses")
        if organizations != "":
            options.append("::CONTENT-XML-CHECKBOX::Professional Organizations, Committees, and Boards")
        if hobbies != "":
            options.append("::CONTENT-XML-CHECKBOX::Hobbies and Interests")
        if quote != "":
            options.append("::CONTENT-XML-CHECKBOX::Quote")
        if website != "":
            options.append("::CONTENT-XML-CHECKBOX::Website")

        options = ''.join(options)

        data_list = [
            structured_data_node("options", options),
            structured_data_node("biography", escape_wysiwyg_content(biography)),
            structured_data_node("awards", escape_wysiwyg_content(awards)),
            structured_data_node("courses", escape_wysiwyg_content(courses)),
            structured_data_node("publications", escape_wysiwyg_content(publications)),
            structured_data_node("presentations", escape_wysiwyg_content(presentations)),
            structured_data_node("certificates", escape_wysiwyg_content(certificates)),
            structured_data_node("organizations", escape_wysiwyg_content(organizations)),
            structured_data_node("hobbies", escape_wysiwyg_content(hobbies)),
            structured_data_node("quote", quote),
            structured_data_node("website", website),

        ]

        node = {
            'type': "group",
            'identifier': "add-to-bio",
            'structuredDataNodes': {
                'structuredDataNode': data_list,
            },
        }

        return node

    # todo: can be deleted
    def dynamic_field(self, name, values):
        values_list = []
        for value in values:
            values_list.append({'value': value})
        node = {
            'name': name,
            'fieldValues': {
                'fieldValue': values_list,
            },
        }

        return node

    # todo: change this to how e-annz does. Might need to look at create-base-view branch
    def get_faculty_bio_structure(self, add_data, username, faculty_bio_id=None, workflow=None):
        """
         Could this be cleaned up at all?
        """

        # Create Image asset
        image = None

        # todo: clean up getting images
        if 'image_name' in add_data.keys():
            image_name = add_data['image_name']
            image_structure = self.get_image_structure(add_data, "/academics/faculty/images", image_name)
            r = requests.get('https://www.bethel.edu/academics/faculty/images/' + image_name)

            # does this person have a live image already?
            if r.status_code == 404:
                create_image(image_structure)
            else:
                # replace the image on the server already
                image_structure['file']['path'] = "/academics/faculty/images/" + image_name
                from config.config import SOAP_URL, CASCADE_LOGIN as AUTH, SITE_ID
                local_cascade_connection = Cascade(SOAP_URL, AUTH, SITE_ID)
                edit_response = local_cascade_connection.edit(image_structure)

                # publish image
                local_cascade_connection.publish(image_structure['file']['path'], "file")
                app.logger.debug("%s: Image edit/publish: %s %s" % (time.strftime("%c"), username, str(edit_response)))

                # clear the thumbor cache so the new image takes
                clear_resp = clear_image_cache(image_structure['file']['path'])
                app.logger.debug("%s: Images Cleared: %s" % (time.strftime("%c"), clear_resp))
            image = structured_file_data_node('image', "/academics/faculty/images/" + image_name)
        elif 'image_url' in add_data.keys() and add_data['image_url'] is not None and add_data['image_url'] != "":
            # If you don't supply an Image Cascade will clear it out,
            # so create a node out of the existing asset so it maintains the link
            image_name = add_data['image_url'].split('/')[-1]
            image = structured_file_data_node('image', "/academics/faculty/images/" + image_name)

        # Create a list of all the data nodes
        structured_data = [
            structured_data_node("first", add_data['first']),
            structured_data_node("last", add_data['last']),
            structured_data_node("email", add_data['email']),
            structured_data_node("started-at-bethel", add_data['started_at_bethel']),
            self.get_job_titles(add_data),
        ]

        if image:
            structured_data.append(image)

        structured_data.append(self.get_expertise(add_data))
        structured_data.append(self.get_add_a_degree(add_data))
        structured_data.append(self.get_add_to_bio(add_data))
        structured_data.append(self.get_new_job_titles(add_data))

        # Wrap in the required structure for SOAP
        structured_data = {
            'structuredDataNodes': {
                'structuredDataNode': structured_data,
            }
        }

        # create the dynamic metadata dict
        dynamic_fields = {
            'dynamicField': [
                self.dynamic_field('hide-site-nav', ["Hide"]),
            ],
        }

        description = self.build_description(add_data)

        asset = {
            'page': {
                'name': add_data['system_name'],
                'siteId': app.config['SITE_ID'],
                'parentFolderPath': "/academics/faculty",
                'metadataSetPath': "/Robust",
                'contentTypePath': "Academics/Faculty Bio",
                'configurationSetPath': "Faculty Bio",
                # Break this out more once its defined in the form
                'structuredData': structured_data,
                'metadata': {
                    'title': add_data['first'] + " " + add_data['last'],
                    'summary': 'summary',
                    'metaDescription': description,
                    'author': add_data['author'],
                    'dynamicFields': dynamic_fields,
                }
            },
            'workflowConfiguration': workflow
        }

        if faculty_bio_id:
            asset['page']['id'] = faculty_bio_id

        return asset

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

    # this can be deleted, i think
    def get_image_structure(self, add_data, image_dest, image_name, workflow=None):
        image_file = open(app.config['UPLOAD_FOLDER'] + image_name, 'r')
        stream = image_file.read()
        encoded_stream = base64.b64encode(stream)

        asset = {
            'file': {
                'name': image_name,
                'parentFolderPath': image_dest,
                'metadataSetPath': "Images",
                'siteId': app.config['SITE_ID'],
                'siteName': 'Public',
                'data': encoded_stream,
                'metadata': {
                    'metaDescription': "Meet " + add_data['first'] + " " + add_data['last'] + ", " + add_data[
                        'new-job-title1'] + " at Bethel University.",
                }

            },
            'workflowConfiguration': workflow
        }

        return asset

    # todo: this probably doesn't need its own function
    def publish_faculty_bio_xml(self):
        self.publish(app.config['FACULTY_BIO_XML_ID'])

    # todo: this method can be replaced with create() in tinker_controller
    def create_faculty_bio(self, asset):
        auth = app.config['CASCADE_LOGIN']
        client = get_client()

        username = session['username']

        response = client.service.create(auth, asset)
        app.logger.info(time.strftime("%c") + ": Create faculty bio submission by " + username + " " + str(response))

        # publish the xml file so the new bio shows up
        self.publish_faculty_bio_xml()

        return response

    # todo: this method exists in tinker_controller
    def get_add_data(self, lists, form):
        # A dict to populate with all the interesting data.
        add_data = {}

        for key in form.keys():
            if key in lists:
                add_data[key] = form.getlist(key)
            else:
                add_data[key] = form[key]

        # Make it lastname firstname
        system_name = add_data['last'] + " " + add_data['first']

        # Create the system-name from title, all lowercase
        system_name = system_name.lower().replace(' ', '-')

        # Now remove any non a-z, A-Z, 0-9
        system_name = re.sub(r'[^a-zA-Z0-9-]', '', system_name)

        add_data['system_name'] = system_name

        return add_data

    # todo: the generic get_workflow method (can be found in create-base-view branch)
    def get_bio_publish_workflow(self, title="", username="", faculty_bio_id=None, add_data=None):
        schools = []
        for i in range(1, 100):
            try:
                schools.append(add_data['schools' + str(i)])
            finally:
                break

        # only submit workflow if it is a new CAS
        if "College of Arts and Sciences" in schools:
            workflow_id = 'f1638f598c58651313b6fe6b5ed835c5'
        elif "Graduate School" in schools or "College of Adult and Professional Studies" in schools:
            workflow_id = '81dabbc78c5865130c130b3a2b567e75'
        elif "Bethel Seminary" in schools:
            workflow_id = '68ad793e8c5865137c9c2c89440cbbbc'
        else:
            return None

        if faculty_bio_id:
            name = "Faculty Bio Edit - %s" % username
        else:
            name = "New Faculty Bio Submission - %s" % username

        if title:
            name += ": " + title
        workflow = {
            "workflowName": name,
            "workflowDefinitionId": workflow_id,
            "workflowComments": "Faculty Bio Approval Request"
        }

        return workflow

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

    def create_title(self, form_contents):
        title = form_contents['last'] + "-" + form_contents['first']
        title = title.lower().replace(' ', '-')
        return re.sub(r'[^a-zA-Z0-9-]', '', title)

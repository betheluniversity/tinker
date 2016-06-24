# python
import urllib2
import re
import base64
from xml.etree import ElementTree
from operator import itemgetter

# local
from tinker.web_services import *
from tinker.tools import *
from tinker.cascade_tools import *
from tinker import app


def get_expertise(add_data):
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


def get_job_titles(add_data):
    job_titles = []

    # format the dates
    for i in range(1, 200):
        i = str(i)
        try:
            job_title = add_data['job-title' + i]
        except KeyError:
            # This will break once we run out of dates
            break

        job_titles.append(structured_data_node("job-title", job_title))

    return job_titles


def get_new_job_titles(add_data):
    new_job_titles = []

    # format the dates
    for i in range(1, 200):
        undergrad = None
        adult_undergrad = None
        graduate = None
        seminary = None

        dept_chair = None
        program_director = None
        lead_faculty = None
        new_job_title = None

        i = str(i)
        try:
            schools = add_data['schools' + i]
        except KeyError:
            # This will break once we run out of new job titles
            break

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


def get_add_a_degree(add_data):
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


def get_add_to_bio(add_data):

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


def get_faculty_bio_structure(add_data, username, faculty_bio_id=None, workflow=None):
    """
     Could this be cleaned up at all?
    """

    # Create Image asset
    image = None

    if 'image_name' in add_data.keys():
        image_name = add_data['image_name']
        image_structure = get_image_structure(add_data, "/academics/faculty/images", image_name)
        r = requests.get('https://www.bethel.edu/academics/faculty/images/' + image_name)

        # does this person have a live image already?
        if r.status_code == 404:
            create_image(image_structure)
        else:
            # replace the image on the server already
            image_structure['file']['path'] = "/academics/faculty/images/" + image_name
            edit_response = edit(image_structure)

            # publish image
            publish(image_structure['file']['path'], "file")
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
        structured_data_node("deactivate", 'No'),
        structured_data_node("first", add_data['first']),
        structured_data_node("last", add_data['last']),
        structured_data_node("email", add_data['email']),
        structured_data_node("started-at-bethel", add_data['started_at_bethel']),
        get_job_titles(add_data),
    ]
    
    if image:
        structured_data.append(image)

    structured_data.append(get_expertise(add_data))
    structured_data.append(get_add_a_degree(add_data))
    structured_data.append(get_add_to_bio(add_data))
    structured_data.append(get_new_job_titles(add_data))

    # Wrap in the required structure for SOAP
    structured_data = {
        'structuredDataNodes': {
            'structuredDataNode': structured_data,
        }
    }

    # create the dynamic metadata dict
    dynamic_fields = {
        'dynamicField': [
            dynamic_field('hide-site-nav', ["Hide"]),
        ],
    }

    description = build_description(add_data)

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


def build_description(add_data):
    description = "Meet " + add_data['first'] + " " + add_data['last']

    # recurse through all job titles
    schools_found = []
    for i in range(1, 100):
        new_job_title = None

        try:
            schools_found.append(add_data['schools' + str(i)])
        except:
            break

        if 'program-director' + str(i) in add_data and add_data['program-director' + str(i)] == 'Yes':
            new_job_title = 'Program Director'
        elif 'dept-chair' + str(i) in add_data and add_data['dept-chair' + str(i)] == 'Yes':
            new_job_title = 'Department Chair'
        elif 'lead-faculty' + str(i) in add_data and add_data['lead-faculty' + str(i)] != 'Other' and add_data['lead-faculty' + str(i)] is not None:
            new_job_title = add_data['lead-faculty' + str(i)]
        elif 'new-job-title' + str(i) in add_data:
            new_job_title = add_data['new-job-title' + str(i)].strip()
        else:
            break

        punctuation = ', '
        if i == 2 and 'schools3' not in add_data:
            punctuation = ' and '
        elif i >= 3 and 'schools' + str(i+1) not in add_data:
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


def get_image_structure(add_data, image_dest, image_name, workflow=None):

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
                'metaDescription': "Meet " + add_data['first'] + " " + add_data['last'] + ", " + add_data['new-job-title1'] + " at Bethel University.",
            }

        },
        'workflowConfiguration': workflow
    }

    return asset


# A lengthy hardcoded list that maps the metadata values to the Groups on Cascade.
def get_web_author_group(department_metadata):

    # CAS
    if "Anthropology, Sociology, & Reconciliation" == department_metadata:
        return "Anthropology Sociology"
    if "Art & Design" == department_metadata:
        return "Art"
    if "Biblical & Theological Studies" == department_metadata:
        return "Biblical Theological"
    if "Biological Sciences" == department_metadata:
        return "Biology"
    if "Business & Economics" == department_metadata:
        return "Business Economics"
    if "Chemistry" == department_metadata:
        return "Chemistry"
    if "Communication Studies" == department_metadata:
        return "Communication"
    if "Education" == department_metadata:
        return "Education"
    if "English" == department_metadata:
        return "English"
    if "Environmental Studies" == department_metadata:
        return "Environmental Studies"
    if "General Education" == department_metadata:
        return "General Education"
    if "History" == department_metadata:
        return "History"
    if "Honors" == department_metadata:
        return "Honors"
    if "Human Kinetics & Applied Health Science" == department_metadata:
        return "Human Kinetics"
    if "Math & Computer Science" == department_metadata:
        return "Math CS"
    if "Modern World Languages" == department_metadata:
        return "World Languages"
    if "Music" == department_metadata:
        return "Music"
    if "Nursing" == department_metadata:
        return "Nursing"
    if "Philosophy" == department_metadata:
        return "Philosophy"
    if "Physics & Engineering" == department_metadata:
        return "Physics"
    if "Political Science" == department_metadata:
        return "Political Science"
    if "Psychology" == department_metadata:
        return "Psychology"
    if "Social Work" == department_metadata:
        return "Social Work"
    if "Theatre Arts" == department_metadata:
        return "Theatre"

    # Sem
    if "Doctor of Ministry" == department_metadata:
        return "Doctor of Ministry"

    return ""


def create_faculty_bio(asset):

    auth = app.config['CASCADE_LOGIN']
    client = get_client()

    username = session['username']

    response = client.service.create(auth, asset)
    app.logger.info(time.strftime("%c") + ": Create faculty bio submission by " + username + " " + str(response))

    # publish the xml file so the new bio shows up
    publish_faculty_bio_xml()

    return response


def get_faculty_bios_for_user(username):

    if app.config['ENVIRON'] != "prod":
        response = urllib2.urlopen('http://staging.bethel.edu/_shared-content/xml/faculty-bios.xml')
        form_xml = ElementTree.fromstring(response.read())
    else:
        form_xml = ElementTree.parse('/var/www/staging/public/_shared-content/xml/faculty-bios.xml').getroot()
    matches = traverse_faculty_folder(form_xml, username)
    matches = sorted(matches, key=itemgetter('last-name'), reverse=False)

    return matches


def traverse_faculty_folder(traverse_xml, username):
    # if no username is given, then pass over ALL faculty bios
    if username is None:
        matches = []
        for child in traverse_xml.findall('.//system-page'):
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
                # This is a match, add it to array
                matches.append(page_values)
        return matches

    # Traverse an XML folder, adding system-pages to a dict of matches
    user = read(username, "user")
    try:
        allowed_groups = user.asset.user.groups
        allowed_groups = allowed_groups.split(";")
    except AttributeError:
        allowed_groups = []

    matches = []
    for child in traverse_xml.findall('.//system-page'):
        if '_shared-content' not in child.find('path').text:
            # Author check
            try:
                authors = child.find('author')
                if authors is not None:
                    dict_of_authors = authors.text.split(", ")

                    if username in dict_of_authors:
                        page_values = {
                            'author': child.find('author') or None,
                            'id': child.attrib['id'] or "",
                            'title': child.find('title').text or None,
                            'created-on': child.find('created-on').text or None,
                            'path': 'https://www.bethel.edu' + child.find('path').text or "",
                            'last-name': child.find('.//last').text or None,
                            'deactivated': child.find('.//deactivate').text or None
                        }
                        # This is a match, add it to array
                        matches.append(page_values)
                        continue
            # Cascade Group check - by
            finally:
                for md in child.findall("dynamic-metadata"):
                    if (md.find('name').text == 'department' or md.find('name').text == 'seminary-program') and md.find('value') is not None:
                        for allowedGroup in allowed_groups:
                            if allowedGroup == get_web_author_group(md.find('value').text):
                                page_values = {
                                    'author': child.find('author') or None,
                                    'id': child.attrib['id'] or "",
                                    'title': child.find('title').text or None,
                                    'created-on': child.find('created-on').text or None,
                                    'path': 'https://www.bethel.edu' + child.find('path').text or "",
                                    'last-name': child.find('.//last').text or None,
                                    'deactivated': child.find('.//deactivate').text or None
                                }
                                matches.append(page_values)
                                break

                    page_values = group_check(child, allowed_groups)
                    if page_values:
                        matches.append(page_values)
                        break

    return matches


def group_check(child, allowed_groups):
    for allowedGroup in allowed_groups:
        if allowedGroup == 'parlau':
            schools_to_check = ['College of Arts and Sciences']
        elif allowedGroup == 'Faculty Approver - CAPS GS':
            schools_to_check = ['College of Adult and Professional Studies', 'Graduate School']
        elif allowedGroup == 'Faculty Approver - Seminary':
            schools_to_check = ['Bethel Seminary']
        else:
            continue

        school_check = child.find('system-data-structure/job-titles/school')
        # new job titles
        if child.find('system-data-structure/job-titles/school') is not None and school_check.text in schools_to_check:
            page_values = {
                'author': child.find('author') or None,
                'id': child.attrib['id'] or "",
                'title': child.find('title').text or None,
                'created-on': child.find('created-on').text or None,
                'path': 'https://www.bethel.edu' + child.find('path').text or "",
                'last-name': child.find('.//last').text or None,
                'deactivated': child.find('.//deactivate').text or None
            }
            return page_values
        else:  # old job titles -- delete someday
            for md in child.find('dynamic-metadata'):
                if md.find('name') is not None and md.find('name').text == 'school':
                    if md.find('value').text in schools_to_check:
                        page_values = {
                            'author': child.find('author') or None,
                            'id': child.attrib['id'] or "",
                            'title': child.find('title').text or None,
                            'created-on': child.find('created-on').text or None,
                            'path': 'https://www.bethel.edu' + child.find('path').text or "",
                            'last-name': child.find('.//last').text or None,
                            'deactivated': child.find('.//deactivate').text or None
                        }
                        return page_values
    return False


def get_add_data(lists, form):

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


def get_bio_publish_workflow(title="", username="", faculty_bio_id=None, add_data=None):
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


def get_description_text(depts):
    final_dept = None

    # get depts
    for dept in depts:
        for item in dept:
            if item != "None" and item != "Select":
                final_dept = item

    return final_dept

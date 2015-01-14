# python
import urllib2
import re
import base64
from xml.etree import ElementTree

# local
from tinker.web_services import *
from tinker.tools import *
from tinker.cascade_tools import *
from tinker import app


def get_expertise(add_data):
    areas = add_data['areas']
    interests = add_data['research_interests']
    teaching = add_data['teaching_specialty']

    if areas != "":
        select = "Areas of expertise"
    elif interests != "":
        select = "Research Interests"
    elif teaching != "":
        select = "Teaching Speciality"
    else:
        select = "Select"

    data_list = [
        structured_data_node("heading", select),
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
    publications = ""
    certificates = ""
    hobbies = ""
    quote = ""
    website = ""

    if add_data['biography'] is not None:
        biography = add_data['biography']
    if add_data['awards'] is not None:
        awards = add_data['awards']
    if add_data['publications'] is not None:
        publications = add_data['publications']
    if add_data['certificates'] is not None:
        certificates = add_data['certificates']
    if add_data['hobbies'] is not None:
        hobbies = add_data['hobbies']
    if add_data['quote'] is not None:
        quote = add_data['quote']
    if add_data['website'] is not None:
        website = add_data['website']

    if biography != "":
        options.append("::CONTENT-XML-CHECKBOX::Biography")
    if awards != "":
        options.append("::CONTENT-XML-CHECKBOX::Awards")
    if publications != "":
        options.append("::CONTENT-XML-CHECKBOX::Publications")
    if certificates != "":
        options.append("::CONTENT-XML-CHECKBOX::Certificates and Licenses")
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
        structured_data_node("publications", escape_wysiwyg_content(publications)),
        structured_data_node("certificates", escape_wysiwyg_content(certificates)),
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
    if "FACULTY-CAS" not in session['roles'] or 'Tinker Redirects' in session['groups']:
        try:
            image = add_data['image_name']
        except KeyError:
            image = None
        if image:
            image_structure = get_image_structure("/academics/faculty/images", add_data['image_name'])
            r = requests.get('https://www.bethel.edu/academics/faculty/images/' + add_data['image_name'])

            # does this person have a live image already?
            if r.status_code == 404:
                create_image(image_structure)
            else:
                # replace the image on the server already
                image_structure['file']['path'] = "/academics/faculty/images/" + add_data['image_name']
                edit_response = edit(image_structure)

                # publish image
                publish(image_structure['file']['path'], "file")
                app.logger.warn("%s: Image edit/publish: %s %s" % (time.strftime("%c"), username, str(edit_response)))

                # clear the thumbor cache so the new image takes
                clear_resp = clear_image_cache(image_structure['file']['path'])
                app.logger.warn("%s: Images Cleared: %s" % (time.strftime("%c"), clear_resp))
            image = structured_file_data_node('image', "/academics/faculty/images/" + add_data['image_name'])
        elif add_data['image_url'] is not None:
            # If you don't supply an Image Cascade will clear it out,
            # so create a node out of the existing asset so it maintains the link
            image_name = add_data['image_url'].split('/')[-1]
            image = structured_file_data_node('image', "/academics/faculty/images/" + image_name)
    else:
        image = None

    # Create a list of all the data nodes
    structured_data = [
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
    # Wrap in the required structure for SOAP
    structured_data = {
        'structuredDataNodes': {
            'structuredDataNode': structured_data,
        }
    }

    # create the dynamic metadata dict
    dynamic_fields = {
        'dynamicField': [
            dynamic_field('school', add_data['school']),
            dynamic_field('department', add_data['department']),
            dynamic_field('adult-undergrad-program', add_data['adult_undergrad_program']),
            dynamic_field('graduate-program', add_data['graduate_program']),
            dynamic_field('seminary-program', add_data['seminary_program'])
        ],
    }

    depts = [add_data['department'], add_data['adult_undergrad_program'], add_data['graduate_program'], add_data['seminary_program']]

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
                'metaDescription': "Meet " + add_data['first'] + " " + add_data['last'] + ", " + add_data['job-title1'] + " at Bethel University.",
                'author': add_data['author'],
                'dynamicFields': dynamic_fields,
            }
        },
        'workflowConfiguration': workflow
    }

    if faculty_bio_id:
        asset['page']['id'] = faculty_bio_id

    return asset


# A test to see if we can create images in cascade.
def get_image_structure(image_dest, image_name, workflow=None):

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
        },
        'workflowConfiguration': workflow
    }

    return asset


def create_image(asset):
    auth = app.config['CASCADE_LOGIN']
    client = get_client()

    username = session['username']

    response = client.service.create(auth, asset)
    app.logger.warn(time.strftime("%c") + ": Create image submission by " + username + " " + str(response))

    # Publish
    publish(response.createdAssetId, "file")

    return response


# A lengthy hardcoded list that maps the metadata values to the Groups on Cascade.
def get_web_author_group(department_metadata):

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

    return ""


def create_faculty_bio(asset):
    auth = app.config['CASCADE_LOGIN']
    client = get_client()

    username = session['username']

    response = client.service.create(auth, asset)
    app.logger.warn(time.strftime("%c") + ": Create faculty bio submission by " + username + " " + str(response))

    # publish the xml file so the new event shows up
    publish_faculty_bio_xml()

    return response


def get_faculty_bios_for_user(username):

    if app.config['ENVIRON'] != "prod":
        response = urllib2.urlopen('http://staging.bethel.edu/_shared-content/xml/faculty-bios.xml')
        form_xml = ElementTree.fromstring(response.read())
    else:
        form_xml = ElementTree.parse('/var/www/staging/public/_shared-content/xml/faculty-bios.xml').getroot()
    matches = traverse_faculty_folder(form_xml, username)

    return matches


def traverse_faculty_folder(traverse_xml, username):
    ## if no username is given, then pass over ALL faculty bios
    if username == None:
        matches = []
        for child in traverse_xml.findall('.//system-page'):

            page_values = {
                'author': child.find('author') or None,
                'id': child.attrib['id'] or "",
                'title': child.find('title') or None,
                'created-on': child.find('created-on').text or None,
                'path': 'https://www.bethel.edu' + child.find('path').text or "",
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
        try:
            authors = child.find('author')
            if authors is not None:

                dict_of_authors = authors.text.split(", ")

                if username in dict_of_authors:
                    page_values = {
                        'author': child.find('author').text,
                        'id': child.attrib['id'] or "",
                        'title': child.find('title').text or None,
                        'created-on': child.find('created-on').text or None,
                        'path': 'https://www.bethel.edu' + child.find('path').text or "",
                    }
                    # This is a match, add it to array
                    matches.append(page_values)
                    continue
        finally:
            for md in child.findall("dynamic-metadata"):
                if md.find('name').text == 'department' and md.find('value') is not None:
                    for allowedGroup in allowed_groups:

                        if allowedGroup == get_web_author_group(md.find('value').text):

                            page_values = {
                                'author': child.find('author') or None,
                                'id': child.attrib['id'] or "",
                                'title': child.find('title').text or None,
                                'created-on': child.find('created-on').text or None,
                                'path': 'https://www.bethel.edu' + child.find('path').text or "",
                            }
                            matches.append(page_values)
                            break
    return matches


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


def get_bio_publish_workflow(title="", username="", school=None):
    if not school:
        school = []
    if "College of Arts & Sciences" in school:
        workflow_id = 'f1638f598c58651313b6fe6b5ed835c5'
    elif "Graduate School" in school or "College of Adult & Professional Studies" in school:
        workflow_id = '81dabbc78c5865130c130b3a2b567e75'
    else:
        workflow_id = ''

    name = "New Bio Submission - %s" % username
    if title:
        name += ": " + title
    workflow = {
        "workflowName": name,
        "workflowDefinitionId": workflow_id,
        "workflowComments": "New Faculty Bio submission"
    }
    return workflow


def check_publish_sets(school, faculty_bio_id):
    for item in school:
        if item == "College of Arts & Sciences":
            publish("f580ac758c58651313b6fe6bced65fea", "publishset")
            publish(faculty_bio_id)
        if item == "Graduate Schol":
            publish("2ecbad1a8c5865132b2dadea8cdcb2be", "publishset")
        if item == "College of Adult & Professional Studies":
            publish("2ed0beef8c5865132b2dadea1ccf543e", "publishset")
        if item == "Bethel Seminary":
            publish("2ed19c8d8c5865132b2dadea60403657", "publishset")


def get_description_text( depts):
    final_dept = None

    ## get depts
    for dept in depts:
        for item in dept:
            if item != "None" and item != "Select":
                final_dept = item

    return final_dept

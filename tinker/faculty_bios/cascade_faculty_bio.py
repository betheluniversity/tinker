#python
import re
import urllib2
import HTMLParser
from xml.etree import ElementTree as ET

#flask

#local
from tinker.web_services import *

from tinker.cascade_tools import *
from tinker import app
from tinker import tools
##from tinker import cache


def get_job_titles( add_data):
    job_titles = []

    ##format the dates
    for i in range(1, 200):
        i = str(i)
        try:
            job_title = add_data['job-title' + i]
        except KeyError:
            ##This will break once we run out of dates
            break

        job_titles.append( structured_data_node("job-title", job_title ))

    return job_titles

def get_expertise(add_data):
    areas = add_data['areas']
    interests = add_data['research_interests']
    teaching = add_data['teaching_specialty']

    if areas != "" :
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
    },

    return node

def get_add_a_degree(add_data):
    degrees = []

    ##format the dates
    for i in range(1, 200):
        i = str(i)
        try:
            school = 'school' + i
            degree = 'degree-earned' + i
            year = 'year' + i

            degree = add_data[degree]
            school = add_data[school]
            year = add_data[year]

        except KeyError:
            ##This will break once we run out of dates
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
        },

        node = {
            'type': "group",
            'identifier': "education",
            'structuredDataNodes': {
                'structuredDataNode': node,
            },
        },

        degrees.append(node)

    return degrees


def get_add_to_bio(add_data):

    options = []

    biography = add_data['biography']
    awards = add_data['awards']
    publications = add_data['publications']
    certificates = add_data['certificates']
    hobbies = add_data['hobbies']
    quote = add_data['quote']
    website = add_data['website']

    if biography != "" :
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
        structured_data_node("biography", escape_wysiwyg_content(biography) ),
        structured_data_node("awards", escape_wysiwyg_content(awards) ),
        structured_data_node("publications", escape_wysiwyg_content(publications) ),
        structured_data_node("certificates", escape_wysiwyg_content(certificates) ),
        structured_data_node("hobbies", escape_wysiwyg_content(hobbies) ),
        structured_data_node("quote", quote),
        structured_data_node("website", website),

    ]

    node = {
        'type': "group",
        'identifier': "add-to-bio",
        'structuredDataNodes': {
            'structuredDataNode': data_list,
        },
    },

    return node


def get_faculty_bio_structure(add_data, username, faculty_bio_id=None, workflow=None):
    """
     Could this be cleaned up at all?
    """


    ## Create a list of all the data nodes
    structured_data = [
        structured_data_node("email", add_data['email']),
        structured_data_node("started-at-bethel", add_data['started_at_bethel']),
        get_job_titles(add_data),

    ]

    structured_data.extend( get_expertise(add_data) )
    structured_data.extend( get_add_a_degree(add_data) )
    structured_data.extend( get_add_to_bio(add_data) )

    ## Wrap in the required structure for SOAP
    structured_data = {
        'structuredDataNodes': {
            'structuredDataNode': structured_data,
        }
    }

    #create the dynamic metadata dict
    dynamic_fields = {
        'dynamicField': [
            dynamic_field('school', add_data['school']),
            dynamic_field('department', add_data['department']),
            # dynamic_field('adult-undergrad-program', add_data['adult_undergrad_program']),
            # dynamic_field('graduate-program', add_data['graduate_program']),
            # dynamic_field('seminary-program', add_data['seminary_program'])
        ],
    }

    asset = {
        'page': {
            'name': add_data['system_name'],
            'siteId': app.config['SITE_ID'],
            'parentFolderPath': "/academics/faculty",
            'metadataSetPath': "/Robust",
            'contentTypePath': "Academics/Faculty Bio",
            'configurationSetPath': "Faculty Bio",
            ## Break this out more once its defined in the form
            'structuredData': structured_data,
            'metadata': {
                'title': add_data['title'],
                'summary': 'summary',
                'author': add_data['author'] + get_author_groups_by_metadata(add_data['department']),
                'dynamicFields': dynamic_fields,
            }
        },
        'workflowConfiguration': workflow
    }

    if faculty_bio_id:
        asset['page']['id'] = faculty_bio_id

    return asset


## A lengthy hardcoded list that maps the metadata values to the Groups on Cascade.
def get_author_groups_by_metadata(departmentMetadata):
    addAuthors = ""

    if any("Anthropology, Sociology, & Reconciliation" in check for check in departmentMetadata):
        addAuthors += ", Anthropology Sociology"
    if any("Art & Design" in check for check in departmentMetadata):
        addAuthors += ", Art"
    if any("Biblical & Theological Studies" in check for check in departmentMetadata):
        addAuthors += ", Biblical Theological"
    if any("Biological Sciences" in check for check in departmentMetadata):
        addAuthors += ", Biology"
    if any("Business & Economics" in check for check in departmentMetadata):
        addAuthors += ", Business Economics"
    if any("Chemistry" in check for check in departmentMetadata):
        addAuthors += ", Chemistry"
    if any("Communication Studies" in check for check in departmentMetadata):
        addAuthors += ", Communication"
    if any("Education" in check for check in departmentMetadata):
        addAuthors += ", Education"
    if any("English" in check for check in departmentMetadata):
        addAuthors += ", English"
    if any("Environmental Studies" in check for check in departmentMetadata):
        addAuthors += ", Environmental Studies"
    if any("General Education" in check for check in departmentMetadata):
        addAuthors += ", General Education"
    if any("History" in check for check in departmentMetadata):
        addAuthors += ", History"
    if any("Honors" in check for check in departmentMetadata):
        addAuthors += ", Honors"
    if any("Human Kinetics & Applied Health Science" in check for check in departmentMetadata):
        addAuthors += ", Human Kinetics"
    if any("Math & Computer Science" in check for check in departmentMetadata):
        addAuthors += ", Math CS"
    if any("Modern World Languages" in check for check in departmentMetadata):
        addAuthors += ", World Languages"
    if any("Music" in check for check in departmentMetadata):
        addAuthors += ", Music"
    if any("Nursing" in check for check in departmentMetadata):
        addAuthors += ", Anthropology Sociology"
    if any("Philosophy" in check for check in departmentMetadata):
        addAuthors += ", Philosophy"
    if any("Physics & Engineering" in check for check in departmentMetadata):
        addAuthors += ", Physics"
    if any("Political Science" in check for check in departmentMetadata):
        addAuthors += ", Political Science"
    if any("Psychology" in check for check in departmentMetadata):
        addAuthors += ", Psychology"
    if any("Social Work" in check for check in departmentMetadata):
        addAuthors += ", Social Work"
    if any("Theatre Arts" in check for check in departmentMetadata):
        addAuthors += ", Theatre"

    return addAuthors


def create_faculty_bio(asset):
    auth = app.config['CASCADE_LOGIN']
    client = get_client()

    username = tools.get_user()

    response = client.service.create(auth, asset)
    app.logger.warn(time.strftime("%c") + ": Create faculty bio submission by " + username + " " + str(response))
    ##publish the xml file so the new event shows up
    publish_faculty_bio_xml()


    return response


def get_faculty_bios_for_user(username):

    if app.config['ENVIRON'] != "prod":
        response = urllib2.urlopen('http://staging.bethel.edu/_shared-content/xml/faculty-bios.xml')
        form_xml = ET.fromstring(response.read())
    else:
        form_xml = ET.parse('/var/www/staging/public/_shared-content/xml/faculty-bios.xml').getroot()
    matches = traverse_faculty_folder(form_xml, username)

    return matches

def traverse_faculty_folder(traverse_xml, username):
    ## Travserse an XML folder, adding system-pages to a dict of matches
    user = read( username , "user")
    allowedGroups = user.asset.user.groups
    allowedGroups = allowedGroups.split(";")

    matches = []
    for child in traverse_xml:
        if child.tag == 'system-page':
            try:
                authors = child.find('author').text
                authors = authors.split( ", ")
            except AttributeError:
                continue

            try:
                is_published = child.find('last-published-on').text
            except AttributeError:
                is_published = False



            for author in authors:

                if author == username:
                    page_values = {
                        'author': child.find('author').text,
                        'id': child.attrib['id'] or None,
                        'title': child.find('title').text or None,
                        'created-on': child.find('created-on').text or None,
                        'path': 'http://staging.bethel.edu' + child.find('path').text or None,
                        'is_published': is_published
                    }
                    ## This is a match, add it to array
                    matches.append(page_values)
                else:
                    for allowedGroup in allowedGroups:
                        if allowedGroup == author:


                            page_values = {
                                'author': child.find('author').text,
                                'id': child.attrib['id'] or None,
                                'title': child.find('title').text or None,
                                'created-on': child.find('created-on').text or None,
                                'path': 'http://staging.bethel.edu' + child.find('path').text or None,
                                'is_published': is_published
                            }
                            ## This is a match, add it to array
                            matches.append(page_values)


        elif child.tag == 'system-folder':
            ##recurse into the page
            matches.extend(traverse_faculty_folder(child, username))
    return matches

def get_add_data(lists, form):

    ##A dict to populate with all the interesting data.
    add_data = {}

    for key in form.keys():
        if key in lists:
            add_data[key] = form.getlist(key)
        else:
            add_data[key] = form[key]

    ##Create the system-name from title, all lowercase
    system_name = add_data['title'].lower().replace(' ', '-')

    ##Now remove any non a-z, A-Z, 0-9
    system_name = re.sub(r'[^a-zA-Z0-9-]', '', system_name)

    add_data['system_name'] = system_name

    return add_data


def get_bio_publish_workflow(title="", username=""):

    name = "New Bio Submission"
    if title:
        name += ": " + title
    workflow = {
        "workflowName": name,
        "workflowDefinitionId": "6085e51c8c5865135c5c083d467cbae5",
        "workflowComments": "New Faculty Bio submission"
    }
    return workflow
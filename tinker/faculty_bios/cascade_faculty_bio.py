#python
import urllib2
import re
from xml.etree import ElementTree as ET
from xml.dom.minidom import parseString
#flask

#local
from tinker.web_services import *

from tinker.cascade_tools import *
from tinker import app
from tinker import tools

##from tinker import cache

def get_xml_bios(url):
    file = urllib2.urlopen(url)

    data = file.read()

    file.close()

    dom = parseString(data)

    pages = dom.getElementsByTagName('system-page')


    return pages

    # print xmlData

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
                'author': add_data['author'],
                'dynamicFields': dynamic_fields,
            }
        },
        'workflowConfiguration': workflow
    }

    if faculty_bio_id:
        asset['page']['id'] = faculty_bio_id

    return asset


## A lengthy hardcoded list that maps the metadata values to the Groups on Cascade.
def get_web_author_group(departmentMetadata):

    if "Anthropology, Sociology, & Reconciliation" == departmentMetadata:
        return "Anthropology Sociology"
    if "Art & Design" == departmentMetadata:
        return "Art"
    if "Biblical & Theological Studies" == departmentMetadata:
        return "Biblical Theological"
    if "Biological Sciences" == departmentMetadata:
        return "Biology"
    if "Business & Economics" == departmentMetadata:
        return "Business Economics"
    if "Chemistry" == departmentMetadata:
        return "Chemistry"
    if "Communication Studies" == departmentMetadata:
        return "Communication"
    if "Education" == departmentMetadata:
        return "Education"
    if "English" == departmentMetadata:
        return "English"
    if "Environmental Studies" == departmentMetadata:
        return "Environmental Studies"
    if "General Education" == departmentMetadata:
        return "General Education"
    if "History" == departmentMetadata:
        return "History"
    if "Honors" == departmentMetadata:
        return "Honors"
    if "Human Kinetics & Applied Health Science" == departmentMetadata:
        return "Human Kinetics"
    if "Math & Computer Science" == departmentMetadata:
        return "Math CS"
    if "Modern World Languages" == departmentMetadata:
        return "World Languages"
    if "Music" == departmentMetadata:
        return "Music"
    if "Nursing" == departmentMetadata:
        return "Anthropology Sociology"
    if "Philosophy" == departmentMetadata:
        return "Philosophy"
    if "Physics & Engineering" == departmentMetadata:
        return "Physics"
    if "Political Science" == departmentMetadata:
        return "Political Science"
    if "Psychology" == departmentMetadata:
        return "Psychology"
    if "Social Work" == departmentMetadata:
        return "Social Work"
    if "Theatre Arts" == departmentMetadata:
        return "Theatre"

    return ""


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

## Function to get the values from xml.
def get_page_values_from_xml(page, authors_text ):
    title_text = ""
    if len(page.getElementsByTagName('title')) > 0:
        title = page.getElementsByTagName('title')[0].toxml()
        title_text = title.replace('<title>','').replace('</title>','')

    created_text = ""
    if len(page.getElementsByTagName('created-on')) > 0:
        created = page.getElementsByTagName('created-on')[0].toxml()
        created_text = created.replace('<created-on>','').replace('</created-on>','')

    path_text = ""
    if len(page.getElementsByTagName('path')) > 0:
        path = page.getElementsByTagName('path')[0].toxml()
        path_text = 'http://staging.bethel.edu' + path.replace('<path>','').replace('</path>','')

    is_published_text = True
    if len(page.getElementsByTagName('last-published-on')) > 0:
        published = page.getElementsByTagName('last-published-on')[0].toxml()
    else:
        is_published_text = False
        path_text = ""

    page_values = {
        'author': authors_text,
        'id': page.getAttribute('id') or None,
        'title': title_text or None,
        'created-on': created_text or None,
        'path': path_text or '',
        'is_published': is_published_text
    }
    return page_values


def traverse_faculty_folder(traverse_xml, username):
    ## Traverse an XML folder, adding system-pages to a dict of matches
    user = read(username, "user")
    try:
        allowedGroups = user.asset.user.groups
        allowedGroups = allowedGroups.split(";")
    except AttributeError:
        allowedGroups = []

    ## Todo: This function can be removed. The 'traverse_xml' variable above is already doing that.
    pages = get_xml_bios("http://www.bethel.edu/_shared-content/xml/faculty-bios.xml")
    matches = []

    for page in pages:
        added_page = False
        try:

            ## check if author matches
            if len(page.getElementsByTagName('author')) > 0:
                authors = page.getElementsByTagName('author')[0].toxml()
                authors_text = authors.replace('<author>','').replace('</author>','')

                authors = authors.split( ", ")

                for author in authors:
                    if username == authors_text:
                        page_values = get_page_values_from_xml(page, authors_text);
                        ## This is a match, add it to array
                        matches.append(page_values)
                        added_page = True
                        break


            ## check if metadata matches
            ## This got really nasty traversing and checking on the way down the list.
            ## Todo: It is probably worth cleaning this up.
            mds = page.getElementsByTagName('dynamic-metadata')
            for md in mds:
                if added_page != True:                                                                                  ## if you already added this page, skip this!
                    if len(md.getElementsByTagName('name')) > 0 and len(md.getElementsByTagName('value')) > 0:          ## make sure the elements exist
                        if md.getElementsByTagName('name')[0].toxml() == '<name>department</name>':                     ## make sure the metadata name is department
                            dept_value = md.getElementsByTagName('value')[0].toxml()
                            dept_value = dept_value.replace('<value>','').replace('</value>','').replace('amp;', '')

                            if dept_value != 'Select':
                                for allowedGroup in allowedGroups:

                                    if allowedGroup == get_web_author_group(dept_value):
                                        page_values = get_page_values_from_xml(page, authors_text);
                                        matches.append(page_values)
                                        added_page = True
                                        break

        except AttributeError:
            continue
    return matches

def get_add_data(lists, form):

    ##A dict to populate with all the interesting data.
    add_data = {}

    for key in form.keys():
        if key in lists:
            add_data[key] = form.getlist(key)
        else:
            add_data[key] = form[key]

    ##Make it lastname firstname
    system_name = add_data['title'].split(" ", 1)
    system_name = system_name[1] + " " + system_name[0]

    ##Create the system-name from title, all lowercase
    system_name = system_name.lower().replace(' ', '-')

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

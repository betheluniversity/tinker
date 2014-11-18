#python
import urllib2
import re
from xml.etree import ElementTree as ET

#local
from tinker.web_services import *
from tinker import app
from tinker.cascade_tools import *


def get_e_announcements_for_user(username):

    if app.config['ENVIRON'] != "prod":
        response = urllib2.urlopen('http://staging.bethel.edu/_shared-content/xml/e-announcements.xml')
        form_xml = ET.fromstring(response.read())
    else:
        form_xml = ET.parse('/var/www/staging/public/_shared-content/xml/e-announcements.xml').getroot()
    matches = traverse_e_announcements_folder(form_xml, username)

    return matches


def traverse_e_announcements_folder(traverse_xml, username):
    ## Traverse an XML folder, adding system-pages to a dict of matches



    matches = []
    for child in traverse_xml.findall('.//system-page'):
        try:
            author = child.find('author').text

            first = child.find('system-data-structure/first-date').text
            second = child.find('system-data-structure/second-date').text
            firstDate = datetime.datetime.strptime(first, '%m-%d-%Y').strftime('%A %B %d, %Y')
            secondDate = datetime.datetime.strptime(second, '%m-%d-%Y').strftime('%A %B %d, %Y')


            dates_str = firstDate + "<br/>" + secondDate

            if author is not None and username == author:
                page_values = {
                    'author': child.find('author').text,
                    'id': child.attrib['id'] or "",
                    'title': child.find('title').text or None,
                    'created-on': child.find('created-on').text or None,
                    'path': 'https://www.bethel.edu' + child.find('path').text or "",
                    'dates': dates_str,
                }
                ## This is a match, add it to array
                matches.append(page_values)
        except:
            continue
        if child.tag == 'system-folder':
            matches.extend(traverse_e_announcements_folder(child, username))
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


def get_e_announcement_structure(add_data, username, workflow=None, e_announcement_id=None):
    """
     Could this be cleaned up at all?
    """

    ## Create a list of all the data nodes
    structured_data = [
        structured_data_node("message", add_data['message']),
        structured_data_node("department", add_data['department']),
        structured_data_node("first-date", add_data['first']),
        structured_data_node("second-date", add_data['second']),
    ]

    ## Wrap in the required structure for SOAP
    structured_data = {
        'structuredDataNodes': {
            'structuredDataNode': structured_data,
        }
    }

    #create the dynamic metadata dict
    dynamic_fields = {
        'dynamicField': [
            dynamic_field('banner-roles', add_data['banner_roles']),
        ],
    }

    parentFolder = get_e_announcement_parent_folder(add_data['first'])

    asset = {
        'page': {
            'name': add_data['system_name'],
            'siteId': app.config['SITE_ID'],
            'parentFolderPath': parentFolder,
            'metadataSetPath': "/Targeted",
            'contentTypePath': "E-Announcement",
            'configurationSetPath': "E-Announcement",
            'structuredData': structured_data,
            'metadata': {
                'title': add_data['title'],
                'author': username,
                'dynamicFields': dynamic_fields,
            }
        },
        'workflowConfiguration': workflow
    }

    if e_announcement_id:
        asset['page']['id'] = e_announcement_id

    return asset


## If no folder exists, create one.
def get_e_announcement_parent_folder(date):
    ## break the date into Year/month
    splitDate = date.split("-")
    month = convert_month_num_to_name(splitDate[0])
    year = splitDate[2]

    return "e-announcements/" + year + "/" + month


def create_e_announcement(asset):
    auth = app.config['CASCADE_LOGIN']
    client = get_client()

    username = session['username']

    response = client.service.create(auth, asset)
    app.logger.warn(time.strftime("%c") + ": Create E-Announcement submission by " + username + " " + str(response))
    ##publish the xml file so the new event shows up
    publish_e_announcement_xml()

    return response


def convert_month_num_to_name(month_num):
    if month_num == "01":
        return "january"
    if month_num == "02":
        return "february"
    if month_num == "03":
        return "march"
    if month_num == "04":
        return "april"
    if month_num == "05":
        return "may"
    if month_num == "06":
        return "june"
    if month_num == "07":
        return "july"
    if month_num == "08":
        return "august"
    if month_num == "09":
        return "september"
    if month_num == "10":
        return "october"
    if month_num == "11":
        return "november"
    if month_num == "12":
        return "december"

def get_e_announcement_publish_workflow(title="", username=""):

    name = "New E-announcement Submission"
    if title:
        name += ": " + title
    workflow = {
        "workflowName": name,
        "workflowDefinitionId": "aae9f9678c5865130c130b3a0d785704",
        "workflowComments": "Send e-announcement for approval"
    }
    return workflow
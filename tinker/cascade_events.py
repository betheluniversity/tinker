#python
import re
import datetime


from xml.etree import ElementTree as ET
import urllib2

#local
from tools import *
from web_services import *


def get_event_structure(add_data, username, event_id=None):
    """
     Could this be cleaned up at all?
    """

    ## Create a list of all the data nodes
    structured_data = [
        structured_data_node("main-content", add_data['main_content']),
        structured_data_node("questions", add_data['questions']),
        structured_data_node("cancellations", add_data['cancellations']),
        structured_data_node("registration-details", add_data['registration_details']),
        structured_data_node("registration-heading", add_data['registration_heading']),
        structured_data_node("cost", add_data['cost']),
        structured_data_node("sponsors", add_data['sponsors']),
        structured_data_node("maps-directions", add_data['maps_directions']),
        structured_data_node("off-campus-location", add_data['off_campus_location']),
        structured_data_node("location", add_data['location']),
        structured_data_node("featuring", add_data['featuring']),
        structured_data_node("wufoo-code", add_data['wufoo_code']),


    ]
    ## Add the dates at the end of the data
    structured_data.extend(add_data['dates'])

    ## Wrap in the required structure for SOAP
    structured_data = {
        'structuredDataNodes': {
            'structuredDataNode': structured_data,
        }
    }

    #create the dynamic metadata dict
    dynamic_fields = {
        'dynamicField': [
            dynamic_field('general', add_data['general']),
            dynamic_field('offices', add_data['offices']),
            dynamic_field('academic-dates', add_data['academic_dates']),
            dynamic_field('cas-departments', add_data['cas_departments']),
            dynamic_field('internal', add_data['internal']),
        ],
    }

    #put it all into the final asset with the rest of the SOAP structure
    asset = {
        'page': {
            'name': add_data['system_name'],
            'siteId': "ba134ac58c586513100ee2a7cec27f4a",
            'parentFolderPath': get_folder_path(add_data),
            'metadataSetPath': "/Event",
            'contentTypePath': "/Event",
            'configurationSetPath': "/Event",
            ## Break this out more once its defined in the form
            'structuredData': structured_data,
            'metadata': {
                'title': add_data['title'],
                'summary': 'summary',
                'author': username,
                'metaDescription': add_data['teaser'],
                'dynamicFields': dynamic_fields,
            }
        }
    }

    if event_id:
        asset['page']['id'] = event_id

    return asset


def create(asset):
    auth = app.config['CASCADE_LOGIN']
    client = get_client()
    response = client.service.create(auth, asset)

    ##publish the xml file so the new event shows up
    publish(app.config['EVENT_XML_ID'])

    return response


def edit(asset):

    auth = app.config['CASCADE_LOGIN']
    client = get_client()
    response = client.service.edit(auth, asset)

    ##publish the xml file so the new event shows up
    publish(app.config['EVENT_XML_ID'])

    return response


def traverse_event_folder(traverse_xml, username):
    ## Travserse an XML folder, adding system-pages to a dict of matches

    matches = []
    for child in traverse_xml:
        if child.tag == 'system-page':
            try:
                author = child.find('author').text
            except AttributeError:
                continue

            try:
                is_published = child.find('last-published-on').text
            except AttributeError:
                is_published = False

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

        elif child.tag == 'system-folder':
            ##recurse into the page
            matches.extend(traverse_event_folder(child, username))
    return matches


def get_forms_for_user(username):

    response = urllib2.urlopen('http://staging.bethel.edu/_shared-content/xml/events.xml')
    form_xml = ET.fromstring(response.read())
    matches = traverse_event_folder(form_xml, username)

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


def date_to_java_unix(date):

    return int(datetime.datetime.strptime(date, '%B %d  %Y, %I:%M %p').strftime("%s")) * 1000


def java_unix_to_date(date):

    return datetime.datetime.fromtimestamp(int(date) / 1000).strftime('%B %d  %Y, %I:%M %p')


def get_dates(add_data):

    dates = []

    ##format the dates
    for i in range(1, 200):
        i = str(i)
        try:
            start = 'start' + i
            end = 'end' + i
            all_day = 'allday' + i

            start = add_data[start]
            end = add_data[end]
            all_day = all_day in add_data.keys()

        except KeyError:
            ##This will break once we run out of dates
            break

        #Get rid of the facy formatting so we just have normal numbers
        start = start.replace('th', '').replace('st', '').replace('rd', '').replace('nd', '')
        end = end.replace('th', '').replace('st', '').replace('rd', '').replace('nd', '')

        # Convert to a unix timestamp, and then multiply by 1000 because Cascade uses Java dates
        # which use milliseconds instead of seconds
        try:
            start = date_to_java_unix(start)
        except ValueError:
            start = None
        try:
            end = date_to_java_unix(end)
        except ValueError:
            end = None

        dates.append(event_date(start, end, all_day))

    return dates

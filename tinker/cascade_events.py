#python
import re
import urllib2
from xml.etree import ElementTree as ET

#flask

#local
from web_services import *

from tinker import app
##from tinker import cache

#just duplicate a bunch for now
def string_to_datetime(date_str):

    try:
        return datetime.datetime.strptime(date_str, '%B %d  %Y, %I:%M %p').date()
    except TypeError:
        return None


def read_date_data_dict(node):
    node_data = node['structuredDataNodes']['structuredDataNode']
    date_data = {}
    for date in node_data:
        date_data[date['identifier']] = date['text']
    ##If there is no date, these will fail
    try:
        date_data['start-date'] = java_unix_to_date(date_data['start-date'])
    except TypeError:
        pass
    try:
        date_data['end-date'] = java_unix_to_date(date_data['end-date'])
    except TypeError:
        pass

    return date_data


def read_date_data_structure(node):
    node_data = node.structuredDataNodes.structuredDataNode
    date_data = {}
    for date in node_data:
        date_data[date.identifier] = date.text
    ##If there is no date, these will fail
    try:
        date_data['start-date'] = java_unix_to_date(date_data['start-date'])
    except TypeError:
        pass
    try:
        date_data['end-date'] = java_unix_to_date(date_data['end-date'])
    except TypeError:
        pass

    return date_data


def dynamic_field(name, values):

    values_list = []
    for value in values:
        values_list.append({'value': value})
    node = {
        'name': name,
        'fieldValues': {
            'fieldValue': values_list,
        },
    },

    return node


def structured_data_node(id, text, node_type=None):

    if not node_type:
        node_type = "text"

    node = {

        'identifier': id,
        'text': text,
        'type': node_type,
    }

    return node


def date_to_java_unix(date):

    return int(datetime.datetime.strptime(date, '%B %d  %Y, %I:%M %p').strftime("%s")) * 1000


def java_unix_to_date(date):

    return datetime.datetime.fromtimestamp(int(date) / 1000).strftime('%B %d  %Y, %I:%M %p')


def get_event_structure(add_data, username, workflow=None, event_id=None):
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
        structured_data_node("on-campus-location", add_data['on_campus_location']),
        structured_data_node("other-on-campus", add_data['other_on_campus']),
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
    paths = get_event_folder_path(add_data)

    asset = {
        'page': {
            'name': add_data['system_name'],
            'siteId': app.config['SITE_ID'],
            'parentFolderPath': paths[1],
            'metadataSetPath': "/Event",
            'contentTypePath': paths[0],
            'configurationSetPath': paths[0],
            ## Break this out more once its defined in the form
            'structuredData': structured_data,
            'metadata': {
                'title': add_data['title'],
                'summary': 'summary',
                'author': username,
                'metaDescription': add_data['teaser'],
                'dynamicFields': dynamic_fields,
            }
        },
        'workflowConfiguration': workflow
    }

    if event_id:
        asset['page']['id'] = event_id

    return asset


def create(asset):
    auth = app.config['CASCADE_LOGIN']
    client = get_client()

    response = client.service.create(auth, asset)

    """

    <complexType name="workflow-configuration">
  <sequence>
    <element maxOccurs="1" minOccurs="1" name="workflowName" type="xsd:string"/>
    <choice>
      <element maxOccurs="1" minOccurs="1" name="workflowDefinitionId" type="xsd:string"/>
      <element maxOccurs="1" minOccurs="1" name="workflowDefinitionPath" type="xsd:string"/>
    </choice>
    <element maxOccurs="1" minOccurs="1" name="workflowComments" type="xsd:string"/>
    <element maxOccurs="1" minOccurs="0" name="workflowStepConfigurations" type="impl:workflow-step-configurations"/>
  </sequence>
</complexType>

    """



    ##publish the xml file so the new event shows up
    ##publish_event_xml()

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

    if app.config['ENVIRON'] != "prod":
        response = urllib2.urlopen('http://staging.bethel.edu/_shared-content/xml/events.xml')
        form_xml = ET.fromstring(response.read())
    else:
        form_xml = ET.parse('/var/www/staging/public/_shared-content/xml/events.xml').getroot()
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
        start = start.split(' ')
        end = end.split(' ')
        start[1] = start[1].replace('th', '').replace('st', '').replace('rd', '').replace('nd', '')
        end[1] = end[1].replace('th', '').replace('st', '').replace('rd', '').replace('nd', '')

        start = " ".join(start)
        end = " ".join(end)

        # Convert to a unix timestamp, and then multiply by 1000 because Cascade uses Java dates
        # which use milliseconds instead of seconds
        try:
            start = date_to_java_unix(start)
        except ValueError as e:
            app.logger.error(time.strftime("%c") + ": error converting start date " + str(e))
            start = None
        try:
            end = date_to_java_unix(end)
        except ValueError as e:
            app.logger.error(time.strftime("%c") + ": error converting end date " + str(e))
            end = None

        dates.append(event_date(start, end, all_day))

    return dates


def event_date(start, end, all_day=False):

    date_list = [
        structured_data_node("start-date", start),
        structured_data_node("end-date", end),
    ]
    if all_day:
        date_list.append(structured_data_node("all-day", "::CONTENT-XML-CHECKBOX::Yes"))

    node = {
        'type': "group",
        'identifier': "event-dates",
        'structuredDataNodes': {
            'structuredDataNode': date_list,
        },
    },

    return node

#Returns (content/config path, parent path)
def get_event_folder_path(data):
    #Check to see if this event should go in a specific folder

    def common_elements(list1, list2):
        #helper function to see if two lists share items
        return [element for element in list1 if element in list2]


    #Find the year we want
    max_year = get_year_folder_value(data)

    path = "events/%s" % max_year
    content_config_no_nav_path = "Event No Nav"
    content_config_with_nav_path = "Event With Nav"

    academic_dates = data['academic_dates']
    if len(academic_dates) > 1:
        return [content_config_no_nav_path, path + "/academic-dates"]

    if len(academic_dates) == 1 and academic_dates[0] != "None":
        return [content_config_no_nav_path, path + "/academic-dates"]

    general = data['general']
    if 'Athletics' in general:
        return [content_config_no_nav_path, path + "/athletics"]

    if common_elements(['Johnson Gallery', 'Olson Gallery', 'Art Galleries'],  general):
        return [content_config_with_nav_path, "events/arts/galleries/exhibits/%s" % max_year]

    if 'Music Concerts' in general:
        return [content_config_with_nav_path, 'events/arts/music/%s' % max_year]

    if 'Theatre' in general:
        return [content_config_with_nav_path, 'events/arts/theatre/%s' % max_year]

    offices = data['offices']
    if 'Bethel Student Government' in offices:
        return [content_config_no_nav_path, path + "/bsg"]

    if 'Career Development' in offices:
        return [content_config_no_nav_path, path + "/career-development-calling"]

    if 'Library' in general:
        return [content_config_no_nav_path, path + "/library"]

    return [content_config_no_nav_path, path]


def move_event_year(event_id, data):

    new_path = get_event_folder_path(data)

    resp = move(event_id, new_path)

    return resp


def get_year_folder_value(data):
    dates = data['dates']
    max_year = 0
    for node in dates:
        date_data = read_date_data_dict(node[0])
        end_date = string_to_datetime(date_data['end-date'])
        try:
            year = end_date.year
        except AttributeError:
            #if end_date is none and this fails, revert to current year.
            year = datetime.date.today().year
        if year > max_year:
            max_year = year

    return max_year


def get_current_year_folder(event_id):
    ##read in te page and find the current year
    asset = read(event_id)
    path = asset.asset.page.path
    try:
        year = re.search('events/(\d{4})/', path).group(1)
        return int(year)
    except AttributeError:
        return None


def get_event_delete_workflow():

    workflow = {
        "workflowName": "Delete and unpublish event",
        "workflowDefinitionId": "2099e7f98c586513742d45fdf45eb6e5",
        "workflowComments": "Event Deletion"
    }

    return workflow


def get_event_publish_workflow():
    workflow = {
        "workflowName": "Send event for approval",
        "workflowDefinitionId": "1ca9794e8c586513742d45fd39c5ffe3",
        "workflowComments": "New event submission"
    }

    return workflow
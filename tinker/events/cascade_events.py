# python
import re
import urllib2

from xml.etree import ElementTree as ET
from operator import itemgetter

# local
from tinker.web_services import *
from tinker import app
from tinker.cascade_tools import *
from tinker.tools import *

# just duplicate a bunch for now
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
    # If there is no date, these will fail
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
        if date.identifier == "all-day" and date.text == "::CONTENT-XML-CHECKBOX::":
            continue
        else:
            date_data[date.identifier] = date.text
    # If there is no date, these will fail
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
    }

    return node


def structured_data_node(node_id, text, node_type=None):

    if not node_type:
        node_type = "text"

    node = {

        'identifier': node_id,
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

    # Create Image asset
    if 'image' in add_data.keys() and add_data['image'] is not None and add_data['image'] != "":
        image_node = {
            'identifier': "image",
            'filePath': "/" + add_data['image'],
            'assetType': "file",
            'type': "asset"
        }
    else:
        image_node = None

    # Create a list of all the data nodes
    structured_data = [
        structured_data_node("main-content", escape_wysiwyg_content(add_data['main_content'])),
        structured_data_node("questions", escape_wysiwyg_content(add_data['questions'])),
        structured_data_node("link", escape_wysiwyg_content(add_data['link'])),
        structured_data_node("cancellations", add_data['cancellations']),
        structured_data_node("registration-details", escape_wysiwyg_content(add_data['registration_details'])),
        structured_data_node("registration-heading", add_data['registration_heading']),
        structured_data_node("cost", add_data['cost']),
        structured_data_node("sponsors", add_data['sponsors']),
        structured_data_node("maps-directions", escape_wysiwyg_content(add_data['maps_directions'])),
        structured_data_node("off-campus-location", add_data['off_campus_location']),
        structured_data_node("on-campus-location", add_data['on_campus_location']),
        structured_data_node("other-on-campus", add_data['other_on_campus']),
        structured_data_node("location", add_data['location']),
        structured_data_node("featuring", add_data['featuring']),
        structured_data_node("wufoo-code", add_data['wufoo_code']),
        image_node,
    ]
    # Add the dates at the end of the data
    structured_data.extend(add_data['event-dates'])

    # Wrap in the required structure for SOAP
    structured_data = {
        'structuredDataNodes': {
            'structuredDataNode': structured_data,
        }
    }

    # put it all into the final asset with the rest of the SOAP structure
    hide_site_nav, parentFolderPath = get_event_folder_path(add_data)

    # create the dynamic metadata dict
    dynamic_fields = {
        'dynamicField': [
            dynamic_field('general', add_data['general']),
            dynamic_field('offices', add_data['offices']),
            dynamic_field('cas-departments', add_data['cas_departments']),
            dynamic_field('internal', add_data['internal']),
            dynamic_field('hide-site-nav', [hide_site_nav]),
        ],
    }

    # allows for multiple authors. If none set, default to username
    if 'author' not in add_data or add_data['author'] == "":
        author = username
    else:
        author = add_data['author']

    asset = {
        'page': {
            'name': add_data['system_name'],
            'siteId': app.config['SITE_ID'],
            'parentFolderPath': parentFolderPath,
            'metadataSetPath': "/Event",
            'contentTypePath': "Event",
            'configurationSetPath': "Old/Event",
            # Break this out more once its defined in the form
            'structuredData': structured_data,
            'metadata': {
                'title': add_data['title'],
                'summary': 'summary',
                'author': author,
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

    username = session['username']

    response = client.service.create(auth, asset)
    response = app.logger.warn(time.strftime("%c") + ": New event submission by " + username + " " + str(response))
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

    return response


def create_event_folder(folder_path):
    if folder_path[0] == "/":
        folder_path = folder_path[1:] ## removes the extra "/"

    old_folder_asset = read("/" + folder_path, "folder")

    if 'success = "false"' in str(old_folder_asset):

        array = folder_path.rsplit("/",1)
        parentPath = array[0]
        name = array[1]

        asset = {
            'folder': {
                'metadata':{
                    'title': name,
                    'dynamicFields': {
                        'dynamicField': read_events_base_asset()
                    }
                },
                'metadataSetPath': "Basic",
                'name': name,
                'parentFolderPath': parentPath,
                'siteName': "Public"
            }
        }

        auth = app.config['CASCADE_LOGIN']
        client = get_client()

        username = session['username']

        response = client.service.create(auth, asset)
        response = app.logger.warn(time.strftime("%c") + ": New folder creation by " + username + " " + str(response))
        return True
    return False


def read_events_base_asset():

    base_asset = read("/_cascade/base-assets/folders/event-folder", "folder")
    if 'success = "false"' in str(base_asset):
        return None

    asset = base_asset.asset.folder.metadata.dynamicFields.dynamicField

    ## if there is no metadata, exit
    if len( asset) == 0:
        return None

    dynamic_metadata = []
    for field in asset:
        ## Builds the value string of 1 value
        field_value = None
        if field.fieldValues[0][0].value is not None:
            field_value = str(field.fieldValues[0][0].value)

        ## create the dynamic metadata with values
        dynamic_metadata.append(
            {
                'name': str(field.name),
                'fieldValues': {
                    'fieldValue':
                    [{
                        'value': field_value
                    }]
                }
            })

    return dynamic_metadata


def traverse_event_folder(traverse_xml, username):
    # Travserse an XML folder, adding system-pages to a dict of matches
    # todo use xpath instead of calling this?

    if username == "":
        matches = []
        for child in traverse_xml.findall('.//system-page'):
            author = None
            if child.find('author'):
                author = child.find('author').text

            page_values = {
                'author': author,
                'id': child.attrib['id'] or None,
                'title': child.find('title').text or None,
                'created-on': child.find('created-on').text or None,
            }
            # This is a match, add it to array
            matches.append(page_values)
        return matches


    matches = []
    for child in traverse_xml.findall('.//system-page'):
        try:
            author = child.find('author').text
        except AttributeError:
            continue

        try:
            is_published = child.find('last-published-on').text
        except AttributeError:
            is_published = False

        author = author.replace(" ", "")
        author = author.split(",")

        if username in author:
            dates = child.find('system-data-structure').findall('event-dates')
            dates_str = []
            for date in dates:
                # start = int(date.find('start-date').text) / 1000
                # end = int(date.find('end-date').text) / 1000
                start = int(date.find('start-date').text) / 1000
                end = int(date.find('end-date').text) / 1000
                dates_str.append(friendly_date_range(start, end))

            page_values = {
                'author': child.find('author').text,
                'id': child.attrib['id'] or None,
                'title': child.find('title').text or None,
                'created-on': child.find('created-on').text or None,
                'path': 'https://www.bethel.edu' + child.find('path').text or None,
                'is_published': is_published,
                'event-dates': "<br/>".join(dates_str),
            }
            # This is a match, add it to array
            matches.append(page_values)

    return matches


def get_forms_for_user(username):
    # todo: move this to config
    if app.config['ENVIRON'] != "prod":
        response = urllib2.urlopen('http://staging.bethel.edu/_shared-content/xml/events.xml')
        form_xml = ET.fromstring(response.read())
    else:
        form_xml = ET.parse('/var/www/staging/public/_shared-content/xml/events.xml').getroot()
    matches = traverse_event_folder(form_xml, username)
    matches = sorted(matches, key=itemgetter('title'), reverse=False)

    return matches


def get_forms_for_event_approver():
    # todo: move this to config
    if app.config['ENVIRON'] != "prod":
        response = urllib2.urlopen('http://staging.bethel.edu/_shared-content/xml/events.xml')
        form_xml = ET.fromstring(response.read())
    else:
        form_xml = ET.parse('/var/www/staging/public/_shared-content/xml/events.xml').getroot()

    # Travserse an XML folder, adding system-pages to a dict of matches
    # todo use xpath instead of calling this?

    matches = []
    for child in form_xml.findall('.//system-page'):

        try:
            is_rental = False
            for dynamic_field in child.findall("dynamic-metadata"):
                if dynamic_field.find("name").text == "general":
                    for value in dynamic_field.findall("value"):
                        if value is not None and "Meetings, Conferences and Rentals" == value.text:
                            is_rental = True

        except AttributeError:
            continue

        try:
            author = child.find('author').text
        except AttributeError:
            author = None
        try:
            is_published = child.find('last-published-on').text
        except AttributeError:
            is_published = False

        if is_rental:
            dates = child.find('system-data-structure').findall('event-dates')
            dates_str = []
            for date in dates:
                # start = int(date.find('start-date').text) / 1000
                # end = int(date.find('end-date').text) / 1000
                start = int(date.find('start-date').text) / 1000
                end = int(date.find('end-date').text) / 1000
                dates_str.append(friendly_date_range(start, end))

            page_values = {
                'author': author,
                'id': child.attrib['id'] or None,
                'title': child.find('title').text or None,
                'created-on': child.find('created-on').text or None,
                'path': 'https://www.bethel.edu' + child.find('path').text or None,
                'is_published': is_published,
                'event-dates': "<br/>".join(dates_str),
            }
            # This is a match, add it to array
            matches.append(page_values)


    matches = sorted(matches, key=itemgetter('title'), reverse=False)
    return matches


def get_add_data(lists, form):

    # A dict to populate with all the interesting data.
    add_data = {}

    for key in form.keys():
        if key in lists:
            add_data[key] = form.getlist(key)
        else:
            add_data[key] = form[key]

    # Create the system-name from title, all lowercase
    system_name = add_data['title'].lower().replace(' ', '-')

    # Now remove any non a-z, A-Z, 0-9
    system_name = re.sub(r'[^a-zA-Z0-9-]', '', system_name)

    add_data['system_name'] = system_name

    return add_data


def get_dates(add_data):

    dates = []

    # format the dates
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
            # This will break once we run out of dates
            break

        # Get rid of the facy formatting so we just have normal numbers
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


# Returns (content/config path, parent path)
def get_event_folder_path(data):
    # Check to see if this event should go in a specific folder

    def common_elements(list1, list2):
        # helper function to see if two lists share items
        return [element for element in list1 if element in list2]

    # Find the year we want
    max_year = get_year_folder_value(data)

    path = "events/%s" % max_year
    hide_site_nav = "Hide"

    if 'general' in data:
        general = data['general']
    else:
        general = []

    if 'offices' in data:
        offices = data['offices']
    else:
        offices = []

    if 'Athletics' in general:
        hide_site_nav = "Hide"
        path = "events/%s/athletics" % max_year

    elif common_elements(['Johnson Gallery', 'Olson Gallery', 'Art Galleries'],  general):
        hide_site_nav = "Do not hide"
        path = "events/arts/galleries/exhibits/%s" % max_year

    elif 'Music Concerts' in general:
        hide_site_nav = "Do not hide"
        path = 'events/arts/music/%s' % max_year

    elif 'Theatre' in general:
        hide_site_nav = "Do not hide"
        path = 'events/arts/theatre/%s' % max_year

    elif any("Chapel" in s for s in general):
        hide_site_nav = "Hide"
        path = 'events/%s/chapel' % max_year

    elif 'Library' in general:
        hide_site_nav = "Hide"
        path = "events/%s/library" % max_year

    elif 'Bethel Student Government' in offices:
        hide_site_nav = "Hide"
        path = "events/%s/bsg" % max_year

    elif any("Admissions" in s for s in offices):
        hide_site_nav = "Hide"
        path = 'events/%s/admissions' % max_year

    create_event_folder(path)

    return hide_site_nav, path


def move_event_year(event_id, data):

    new_path = get_event_folder_path(data)

    resp = move(event_id, new_path[1])

    return resp


def get_year_folder_value(data):
    dates = data['event-dates']

    max_year = 0
    for node in dates:
        date_data = read_date_data_dict(node[0])
        end_date = string_to_datetime(date_data['end-date'])
        try:
            year = end_date.year
        except AttributeError:
            # if end_date is none and this fails, revert to current year.
            year = datetime.date.today().year
        if year > max_year:
            max_year = year

    return max_year


def get_current_year_folder(event_id):
    # read in te page and find the current year
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


def get_event_publish_workflow(title="", username=""):
    if title:
        title = "-- %s" % title
    workflow = {
        "workflowName": "%s, %s at %s (%s)" %
                        (title, time.strftime("%m-%d-%Y"), time.strftime("%I:%M %p"), username),
        "workflowDefinitionId": "1ca9794e8c586513742d45fd39c5ffe3",
        "workflowComments": "New event submission"
    }
    return workflow


def publish_event_xml():

    # publish the event XML page
    publish(app.config['EVENT_XML_ID'])



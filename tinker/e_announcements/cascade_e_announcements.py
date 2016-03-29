# python
import urllib2
import re
from xml.etree import ElementTree as ET

# local
from tinker import sentry
from tinker.web_services import *
from tinker.cascade_tools import *
from createsend import *


def get_e_announcements_for_user(username="get_all"):

    if app.config['ENVIRON'] != "prod":
        response = urllib2.urlopen('http://staging.bethel.edu/_shared-content/xml/e-announcements.xml')
        form_xml = ET.fromstring(response.read())
    else:
        form_xml = ET.parse('/var/www/staging/public/_shared-content/xml/e-announcements.xml').getroot()
    matches = traverse_e_announcements_folder(form_xml, username)

    return matches


def recurse(node):
    return_string = ''
    for child in node:
        child_text = ''
        if child.text:
            child_text = child.text

        # recursively renders children
        try:
            if child.tag == 'a':
                return_string += '<%s href="%s">%s%s</%s>' % (child.tag, child.attrib['href'], child_text, recurse(child), child.tag)
            else:
                return_string += '<%s>%s%s</%s>' % (child.tag, child_text, recurse(child), child.tag)
        except:
            # gets the basic text
            if child_text:
                if child.tag == 'a':
                    return_string += '<%s href="%s">%s</%s>' % (child.tag, child.attrib['href'], child_text, child.tag)
                else:
                    return_string += '<%s>%s</%s>' % (child.tag, child_text, child.tag)

        # gets the text that follows the children
        if child.tail:
            return_string += child.tail

    return return_string


def traverse_e_announcements_folder(traverse_xml, username="get_all"):
    # Traverse an XML folder, adding system-pages to a dict of matches

    matches = []
    for child in traverse_xml.findall('.//system-block'):
        try:
            author = child.find('author').text

            if (author is not None and username == author) or username == "get_all":
                first = child.find('system-data-structure/first-date').text
                second = child.find('system-data-structure/second-date').text
                first_date_object = datetime.datetime.strptime(first, '%m-%d-%Y')
                first_date = first_date_object.strftime('%A %B %d, %Y')
                first_date_past = first_date_object < datetime.datetime.now()

                second_date = ''
                second_date_past = ''
                if second:
                    second_date_object = datetime.datetime.strptime(second, '%m-%d-%Y')
                    second_date = second_date_object.strftime('%A %B %d, %Y')
                    second_date_past = second_date_object < datetime.datetime.now()

                roles = []
                values = child.find('dynamic-metadata')
                for value in values:
                    if value.tag == 'value':
                        roles.append(value.text)

                message = ''
                message = recurse(child.find('system-data-structure/message'))

                try:
                    workflow_status = child.find('workflow').find('status').text
                except AttributeError:
                    workflow_status = None

                page_values = {
                    'author': child.find('author').text,
                    'id': child.attrib['id'] or "",
                    'title': child.find('title').text or None,
                    'created-on': child.find('created-on').text or None,
                    'first_date': first_date,
                    'second_date': second_date,
                    'message': message,
                    'roles': roles,
                    'workflow_status': workflow_status,
                    'first_date_past': first_date_past,
                    'second_date_past': second_date_past
                }

                # This is a match, add it to array
                matches.append(page_values)
        except AttributeError:
            sentry.captureException()

    # sort by created-on date.
    matches = sorted(matches, key=lambda k: k['created-on'])

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


def get_e_announcement_structure(add_data, username, workflow=None, e_announcement_id=None):
    """
     Could this be cleaned up at all?
    """

    # Create a list of all the data nodes
    structured_data = [
        structured_data_node("message", escape_wysiwyg_content(add_data['message'])),
        structured_data_node("first-date", add_data['first']),
        structured_data_node("second-date", add_data['second']),
        structured_data_node("name", add_data['name']),
        structured_data_node("email", add_data['email']),
    ]

    # Wrap in the required structure for SOAP
    structured_data = {
        'structuredDataNodes': {
            'structuredDataNode': structured_data,
        },
        'definitionPath': 'E-Announcement'
    }

    # create the dynamic metadata dict
    dynamic_fields = {
        'dynamicField': [
            dynamic_field('banner-roles', add_data['banner_roles']),
        ],
    }

    parent_folder = get_e_announcement_parent_folder(add_data['first'])
    asset = {
        'xhtmlDataDefinitionBlock': {
            'name': add_data['system_name'],
            'siteId': app.config['SITE_ID'],
            'parentFolderPath': parent_folder,
            'metadataSetPath': "/Targeted",
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
        asset['xhtmlDataDefinitionBlock']['id'] = e_announcement_id
        resp = move(e_announcement_id, parent_folder)

    return asset


# if no folder exists, create one.
# this will automatically move the page if the first_date changes.
def get_e_announcement_parent_folder(date):
    # break the date into Year/month
    split_date = date.split("-")
    month = convert_month_num_to_name(split_date[0])
    year = split_date[2]

    # check if the folders exist
    create_e_announcements_folder("e-announcements/" + year)
    create_e_announcements_folder("e-announcements/" + year + "/" + month)

    return "e-announcements/" + year + "/" + month


def create_e_announcements_folder(folder_path):
    if folder_path[0] == "/":
        folder_path = folder_path[1:]  # removes the extra "/"

    old_folder_asset = read("/" + folder_path, "folder")

    if old_folder_asset['success'] == 'false':

        array = folder_path.rsplit("/", 1)
        parent_path = array[0]
        name = array[1]

        asset = {
            'folder': {
                'metadata': {
                    'title': name
                },
                'metadataSetPath': "Basic",
                'name': name,
                'parentFolderPath': parent_path,
                'siteName': "Public"
            }
        }

        auth = app.config['CASCADE_LOGIN']
        client = get_client()

        username = session['username']

        response = client.service.create(auth, asset)
        app.logger.warn(time.strftime("%c") + ": New folder creation by " + username + " " + str(response))
        return True
    return False


def move_e_announcement(id, path):
    resp = move(id, path)
    return resp


def create_e_announcement(asset):
    auth = app.config['CASCADE_LOGIN']
    client = get_client()

    username = session['username']

    response = client.service.create(auth, asset)
    app.logger.warn(time.strftime("%c") + ": Create E-Announcement submission by " + username + " " + str(response))
    # publish the xml file so the new event shows up
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


def get_e_announcement_publish_workflow(title=""):

    name = "New E-announcement Submission"
    if title:
        name += ": " + title
    workflow = {
        "workflowName": name,
        "workflowDefinitionId": app.config['E_ANNOUCNEMENT_WORKFLOW_ID'],
        "workflowComments": "Send e-announcement for approval"
    }
    return workflow


def create_single_announcement(announcement):
    return_value = ''
    count = 1

    for role in announcement['roles']:
        prepended_role = '20322-%s' % role
        if count == 1:
            return_value = '[if:%s=Y]' % prepended_role
        else:
            return_value += '[elseif:%s=Y]' % prepended_role

        return_value += e_announcement_html(announcement)
        count = count+1

    return_value += '[endif]'
    return return_value


def e_announcement_html(announcement):
    element = '''
        <table class="layout layout--no-gutter" style="border-collapse: collapse;table-layout: fixed;Margin-left: auto;Margin-right: auto;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: #ffffff;" align="center" emb-background-style>
            <tbody>
                <tr>
                    <td class="column" style='font-size: 14px;line-height: 21px;padding: 0;text-align: left;vertical-align: top;color: #60666d;font-family: "Open Sans",sans-serif;' width="300">
                        <div style="Margin-left: 20px;Margin-right: 20px;Margin-top: 24px;">
                            <h2 style="Margin-top: 0;Margin-bottom: 0;font-style: normal;font-weight: normal;font-size: 20px;line-height: 28px;color: #555;font-family: sans-serif;">
                                <strong>%s</strong>
                            </h2>
                        </div>
                    </td>
                    <td class="column" style='font-size: 14px;line-height: 21px;padding: 0;text-align: left;vertical-align: top;color: #555;font-family: Georgia,serif' width="600">
                        <div style="Margin-left: 20px;Margin-right: 20px;Margin-top: 24px;Margin-bottom: 24px;">
                            %s
                            <p style="font-family: georgia,serif;font-size: 12px;line-height: 19px;">
                                <span class="font-georgia">
                                    <span style="color:#bdb9bd">
                                        %s
                                    </span>
                                </span>
                            </p>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
      ''' % (announcement['title'], announcement['message'], ', '.join(announcement['roles']))

    return element


# Gets the template IDs
def get_templates_for_client(campaign_monitor_key, client_id):
    for template in Client({'api_key': campaign_monitor_key}, client_id).templates():
        print template.TemplateID


# Checks if the date provided is a valid date
# Valid days are 1) not in the past
#                2) is a M/W/F
#                3) not between 12/24 - 1/1
def check_if_valid_date(date):
    # check if the date is after yesterday at midnight
    if date < datetime.datetime.combine(date.today(), datetime.time.min):
        return False

    # Check if day is mon/wed/fri
    if date.weekday() in [1, 3, 5, 6]:
        return False

    # Check if date is between 12/24 and 1/1
    dates_to_ignore = ['12/24', '12/25', '12/26', '12/27', '12/28', '12/29', '12/30', '12/31', '1/1']
    current_month_day = str(date.month) + '/' + str(date.day)
    if current_month_day in dates_to_ignore:
        return False

    return True
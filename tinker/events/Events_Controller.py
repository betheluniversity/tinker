from tinker.tinker_controller import TinkerController
import json
import datetime
import time

import re
import urllib2
import arrow

from xml.etree import ElementTree as ET
from operator import itemgetter

# local
from tinker import app

from flask import render_template, session

from BeautifulSoup import BeautifulStoneSoup
import cgi


class EventsController(TinkerController):

    def check_event_dates(self, form):
        event_dates = {}
        dates_good = False
        num_dates = int(form['num_dates'])
        for x in range(1, num_dates+1):  # the page doesn't use 0-based indexing

            i = str(x)
            start_l = 'start' + i
            end_l = 'end' + i
            all_day_l = 'allday' + i

            start = form[start_l]
            end = form[end_l]
            all_day = all_day_l in form.keys()

            event_dates[start_l] = start
            event_dates[end_l] = end
            event_dates[all_day_l] = all_day

            start_and_end = start and end

            if start_and_end:
                dates_good = True

        # convert event dates to JSON
        return json.dumps(event_dates), dates_good, num_dates

    def validate_form(self, rform, dates_good, event_dates, num_dates):

        from forms import EventForm
        form = EventForm()

        # todo move to TinkerBase?
        if not form.validate_on_submit() or not dates_good:
            print "inside if statement"
            if 'event_id' in rform.keys():
                event_id = rform['event_id']
            else:
                new_form = True
            # bring in the mapping
            # brm = self.brm
            return render_template('event-form.html', **locals())

    def link(self, add_data, asset):
        # 'link' must be a valid component
        if 'link' in add_data and add_data['link'] != "":
            from tinker.admin.redirects import new_internal_redirect_submit
            path = str(asset['page']['parentFolderPath'] + "/" + asset['page']['name'])
            new_internal_redirect_submit(path, add_data['link'])

        return #????

    def group_callback(self, node):
        data = {}
        type = 'group'

        if node['identifier'] == 'event-dates':
            data[node['date_count']] = self.read_date_data_structure(node)

        return data, type

    def build_edit_form(self, event_id):
        from tinker.events.forms import EventForm

        asset = self.read_page(event_id)
        edit_data, form = self.get_edit_data(asset, EventForm, event_id)
        if edit_data['dates']:
            dates = edit_data['dates']

        return edit_data, form, dates

    # web services methods
    def date_to_java_unix(self, date):

        return int(datetime.datetime.strptime(date, '%B %d  %Y, %I:%M %p').strftime("%s")) * 1000

    def java_unix_to_date(self, date):

        return datetime.datetime.fromtimestamp(int(date) / 1000).strftime('%B %d  %Y, %I:%M %p')

    def friendly_date_range(self, start, end):
        date_format = "%B %d, %Y %I:%M %p"

        start_check = arrow.get(start)
        end_check = arrow.get(end)

        if start_check.year == end_check.year and start_check.month == end_check.month and start_check.day == end_check.day:
            return "%s - %s" % (datetime.datetime.fromtimestamp(int(start)).strftime(date_format),
                                datetime.datetime.fromtimestamp(int(end)).strftime("%I:%M %p"))
        else:
            return "%s - %s" % (datetime.datetime.fromtimestamp(int(start)).strftime(date_format),
                                datetime.datetime.fromtimestamp(int(end)).strftime(date_format))

    # casecade_tools methods
    # todo move
    # Excape content so its Cascade WYSIWYG friendly
    # There are a few edge cases for sybmols it doesn't like.
    def escape_wysiwyg_content(self, content):
        if content:
            uni = self.HTMLEntitiesToUnicode(content)
            htmlent = self.unicodeToHTMLEntities(uni)
            return htmlent
        else:
            return None

    # todo move(?)
    def HTMLEntitiesToUnicode(self, text):
        """Converts HTML entities to unicode.  For example '&amp;' becomes '&'."""
        text = unicode(BeautifulStoneSoup(text, convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
        return text

    # todo move(?)
    def unicodeToHTMLEntities(self, text):
        """Converts unicode to HTML entities.  For example '&' becomes '&amp;'."""
        text = cgi.escape(text).encode('ascii', 'xmlcharrefreplace')
        return text

    # cascade event methods
    def get_forms_for_user(self, username):
        # todo: move this to config
        if app.config['ENVIRON'] != "prod":
            response = urllib2.urlopen('http://staging.bethel.edu/_shared-content/xml/events.xml')
            form_xml = ET.fromstring(response.read())
        else:
            form_xml = ET.parse('/var/www/staging/public/_shared-content/xml/events.xml').getroot()
        matches = self.traverse_event_folder(form_xml, username)
        matches = sorted(matches, key=itemgetter('title'), reverse=False)

        return matches

    def get_forms_for_event_approver(self):
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
                    dates_str.append(self.friendly_date_range(start, end))

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

    def get_event_publish_workflow(self, title="", username=""):
        if title:
            title = "-- %s" % title
        workflow = {
            "workflowName": "%s, %s at %s (%s)" %
                            (title, time.strftime("%m-%d-%Y"), time.strftime("%I:%M %p"), username),
            "workflowDefinitionId": "1ca9794e8c586513742d45fd39c5ffe3",
            "workflowComments": "New event submission"
        }
        return workflow

    def get_add_data(self, lists, form):
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

    def get_dates(self, add_data):
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
                start = self.date_to_java_unix(start)
            except ValueError as e:
                app.logger.error(time.strftime("%c") + ": error converting start date " + str(e))
                start = None
            try:
                end = self.date_to_java_unix(end)
            except ValueError as e:
                app.logger.error(time.strftime("%c") + ": error converting end date " + str(e))
                end = None

            dates.append(self.event_date(start, end, all_day))

        return dates

    def get_event_structure(self, add_data, username, workflow=None, event_id=None):
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
            self.structured_data_node("main-content", self.escape_wysiwyg_content(add_data['main_content'])),
            self.structured_data_node("questions", self.escape_wysiwyg_content(add_data['questions'])),
            self.structured_data_node("link", self.escape_wysiwyg_content(add_data['link'])),
            self.structured_data_node("cancellations", add_data['cancellations']),
            self.structured_data_node("registration-details", self.escape_wysiwyg_content(add_data['registration_details'])),
            self.structured_data_node("registration-heading", add_data['registration_heading']),
            self.structured_data_node("cost", add_data['cost']),
            self.structured_data_node("sponsors", self.escape_wysiwyg_content(add_data['sponsors'])),
            self.structured_data_node("maps-directions", self.escape_wysiwyg_content(add_data['maps_directions'])),
            self.structured_data_node("off-campus-location", add_data['off_campus_location']),
            self.structured_data_node("on-campus-location", add_data['on_campus_location']),
            self.structured_data_node("other-on-campus", add_data['other_on_campus']),
            self.structured_data_node("location", add_data['location']),
            self.structured_data_node("featuring", add_data['featuring']),
            self.structured_data_node("wufoo-code", add_data['wufoo_code']),
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
        hide_site_nav, parent_folder_path = self.get_event_folder_path(add_data)

        # create the dynamic metadata dict
        dynamic_fields = {
            'dynamicField': [
                self.dynamic_field('general', add_data['general']),
                self.dynamic_field('offices', add_data['offices']),
                self.dynamic_field('cas-departments', add_data['cas_departments']),
                self.dynamic_field('graduate-program', add_data['graduate_program']),
                self.dynamic_field('adult-undergrad-program', add_data['adult_undergrad_program']),
                self.dynamic_field('seminary-program', add_data['seminary_program']),
                self.dynamic_field('internal', add_data['internal']),
                self.dynamic_field('hide-site-nav', [hide_site_nav]),
                self.dynamic_field('tinker-edits', '1')
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
                'parentFolderPath': parent_folder_path,
                'metadataSetPath': "/Event",
                'contentTypePath': "Event",
                'configurationSetPath': "Old/Event",
                # Break this out more once its defined in the form
                'structuredData': structured_data,
                'metadata': {
                    'title': add_data['title'],
                    'summary': 'summary',
                    'author': author,
                    'metaDescription': add_data['metaDescription'],
                    'dynamicFields': dynamic_fields,
                }
            },
            'workflowConfiguration': workflow
        }

        if event_id:
            asset['page']['id'] = event_id

        return asset

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

    # Returns (content/config path, parent path)
    def get_event_folder_path(self, data):
        # Check to see if this event should go in a specific folder

        def common_elements(list1, list2):
            # helper function to see if two lists share items
            return [element for element in list1 if element in list2]

        # Find the year we want
        max_year = self.get_year_folder_value(data)

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

        self.copy_folder(path, app.config['EVENTS_FOLDER_ID'])

        return hide_site_nav, path

    def structured_data_node(self, node_id, text, node_type=None):

        if not node_type:
            node_type = "text"

        node = {

            'identifier': node_id,
            'text': text,
            'type': node_type,
        }

        return node

    def get_current_year_folder(self, event_id):
        # read in te page and find the current year
        asset = self.read(event_id, 'page')
        path = asset['asset']['page']['path']
        try:
            year = re.search('events/(\d{4})/', path).group(1)
            return int(year)
        except AttributeError:
            return None

    def get_year_folder_value(self, data):
        dates = data['event-dates']

        max_year = 0
        for node in dates:
            date_data = self.read_date_data_dict(node[0])
            end_date = self.string_to_datetime(date_data['end-date'])
            try:
                year = end_date.year
            except AttributeError:
                # if end_date is none and this fails, revert to current year.
                year = datetime.date.today().year
            if year > max_year:
                max_year = year

        return max_year

    # just duplicate a bunch for now
    def string_to_datetime(self, date_str):

        try:
            return datetime.datetime.strptime(date_str, '%B %d  %Y, %I:%M %p').date()
        except TypeError:
            return None

    def read_date_data_dict(self, node):
        node_data = node['structuredDataNodes']['structuredDataNode']
        date_data = {}
        for date in node_data:
            date_data[date['identifier']] = date['text']
        # If there is no date, these will fail
        try:
            date_data['start-date'] = self.java_unix_to_date(date_data['start-date'])
        except TypeError:
            pass
        try:
            date_data['end-date'] = self.java_unix_to_date(date_data['end-date'])
        except TypeError:
            pass

        return date_data

    def read_date_data_structure(self, node):
        node_data = node['structuredDataNodes']['structuredDataNode']
        date_data = {}
        for date in node_data:
            if date['identifier'] == "all-day" and date['text'] == "::CONTENT-XML-CHECKBOX::":
                continue
            else:
                date_data[date['identifier']] = date['text']
        # If there is no date, these will fail
        try:
            date_data['start-date'] = self.java_unix_to_date(date_data['start-date'])
        except TypeError:
            pass
        try:
            date_data['end-date'] = self.java_unix_to_date(date_data['end-date'])
        except TypeError:
            pass

        return date_data

    def traverse_event_folder(self, traverse_xml, username):
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
                    dates_str.append(self.friendly_date_range(start, end))

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

    def event_date(self, start, end, all_day=False):

        date_list = [
            self.structured_data_node("start-date", start),
            self.structured_data_node("end-date", end),
        ]
        if all_day:
            date_list.append(self.structured_data_node("all-day", "::CONTENT-XML-CHECKBOX::Yes"))

        node = {
            'type': "group",
            'identifier': "event-dates",
            'structuredDataNodes': {
                'structuredDataNode': date_list,
            },
        },

        return node

    def move_event_year(self, event_id, data):
        new_path = self.get_event_folder_path(data)
        resp = self.move(event_id, new_path[1])
        return resp

    def create(self, asset):
        auth = app.config['CASCADE_LOGIN']
        client = self.cascade_connector.get_client()

        username = session['username']

        response = client.service.create(auth, asset)

        from tinker import sentry
        # sentry.captureMessage()

        client = sentry.client

        client.extra_context({
            'Time': time.strftime("%c"),
            'Author': username,
            'Response': str(response)
        })

        self.log_sentry("New event submission", response)
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

from tinker.tinker_controller import TinkerController
import json
from tinker.events.cascade_events import *


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

    def validate_form(self, rform, dates_good):

        from forms import EventForm;
        form = EventForm()

        # todo move to TinkerBase?
        if not form.validate_on_submit() or not dates_good:
            if 'event_id' in rform.keys():
                event_id = rform['event_id']
            else:
                new_form = True
            # bring in the mapping
            brm = self.brm
            return render_template('event-form.html', **locals())

    def link(self, add_data, asset):
        # 'link' must be a valid component
        if 'link' in add_data and add_data['link'] != "":
            from tinker.admin.redirects import new_internal_redirect_submit
            path = str(asset['page']['parentFolderPath'] + "/" + asset['page']['name'])
            new_internal_redirect_submit(path, add_data['link'])

    # todo may not need these next two methods
    # def node(self, s_data, edit_data, date_count, dates):
    #     for node in s_data:
    #         node_identifier = node.identifier.replace('-', '_')
    #         node_type = node.type
    #         if node_type == "text":
    #             edit_data[node_identifier] = node.text
    #         elif node_type == 'group':
    #             # These are the event dates. Create a dict so we can convert to JSON later.
    #             dates[date_count] = read_date_data_structure(node)
    #             date_count += 1
    #         elif node_identifier == 'image':
    #             edit_data['image'] = node.filePath
    #
    # def metadata(self, dynamic_fields, edit_data):
    #     for field in dynamic_fields:
    #         # This will fail if no metadata is set. It should be required but just in case
    #         if field.fieldValues:
    #             items = [item.value for item in field.fieldValues.fieldValue]
    #             edit_data[field.name.replace('-', '_')] = items

    def get_forms_for_user(self, username):
        # todo: move this to config
        if app.config['ENVIRON'] != "prod":
            response = urllib2.urlopen('http://staging.bethel.edu/_shared-content/xml/events.xml')
            form_xml = ET.fromstring(response.read())
        else:
            form_xml = ET.parse('/var/www/staging/public/_shared-content/xml/events.xml').getroot()
        matches = traverse_event_folder(form_xml, username)
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
            structured_data_node("main-content", escape_wysiwyg_content(add_data['main_content'])),
            structured_data_node("questions", escape_wysiwyg_content(add_data['questions'])),
            structured_data_node("link", escape_wysiwyg_content(add_data['link'])),
            structured_data_node("cancellations", add_data['cancellations']),
            structured_data_node("registration-details", escape_wysiwyg_content(add_data['registration_details'])),
            structured_data_node("registration-heading", add_data['registration_heading']),
            structured_data_node("cost", add_data['cost']),
            structured_data_node("sponsors", escape_wysiwyg_content(add_data['sponsors'])),
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
        hide_site_nav, parent_folder_path = get_event_folder_path(add_data)

        # create the dynamic metadata dict
        dynamic_fields = {
            'dynamicField': [
                dynamic_field('general', add_data['general']),
                dynamic_field('offices', add_data['offices']),
                dynamic_field('cas-departments', add_data['cas_departments']),
                dynamic_field('graduate-program', add_data['graduate_program']),
                dynamic_field('adult-undergrad-program', add_data['adult_undergrad_program']),
                dynamic_field('seminary-program', add_data['seminary_program']),
                dynamic_field('internal', add_data['internal']),
                dynamic_field('hide-site-nav', [hide_site_nav]),
                dynamic_field('tinker-edits', '1')
            ],
        }

    def get_current_year_folder(self, event_id):
        # read in te page and find the current year
        asset = read(event_id)
        path = asset.asset.page.path
        try:
            year = re.search('events/(\d{4})/', path).group(1)
            return int(year)
        except AttributeError:
            return None

    def get_year_folder_value(self, data):
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
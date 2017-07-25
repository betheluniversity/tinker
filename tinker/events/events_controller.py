import urllib2
from xml.etree import ElementTree as ET
import json
import datetime
import time
import re
import arrow

# bu-cascade
from bu_cascade.asset_tools import find

# local
from tinker import app
from tinker.tinker_controller import TinkerController

# flask
from flask import render_template, session
from flask import json as fjson


class EventsController(TinkerController):

    def traverse_short_xml(self, xml_url, find_all=False):
        response = urllib2.urlopen(xml_url)
        form_xml = ET.fromstring(response.read())

        matches = []
        for child in form_xml.findall('event'):
            match = self.inspect_child(child, find_all)
            if match:
                matches.append(match)

        # Todo: maybe add some parameter as a search?
        # sort by created-on date.
        matches = sorted(matches, key=lambda k: k['created-on'])
        return matches

    # find_all is currently unused for events (but used for the e-annz)
    def inspect_child(self, child, find_all=False):
        try:
            author = child.find('author').text
            author = author.replace(' ', '').split(',')
        except AttributeError:
            author = None
        username = session['username']

        sem_event = False
        post_trad_event = False
        undergrad_event = False
        if 'Tinker Events - CAS' in session['groups']:
            # Todo: when we move to short-urls
            # undergrad_event = self.search_for_key_in_dynamic_md(child, 'cas-departments')

            for value in child.find('cas-departments').getchildren():
                try:
                    if value.text != 'None':
                        undergrad_event = True
                except:
                    continue

        school_event = undergrad_event or post_trad_event or sem_event

        if (author is not None and username in author) or 'Event Approver' in session['groups'] or (school_event and school_event != 'None'):
            try:
                return self._iterate_child_xml(child, author)
            except AttributeError:
                # not a valid event page
                return None
        else:
            return None

    def split_user_events(self, forms):
        user_forms = []
        other_forms = []
        for form in forms:
            if form['author'] is not None and session['username'] in form['author']:
                user_forms.append(form)
            else:
                other_forms.append(form)
        return user_forms, other_forms

    def check_new_year_folder(self, event_id, add_data, username):
        current_year = self.get_current_year_folder(event_id)
        new_year = self.get_year_folder_value(add_data)
        if new_year > current_year:
            new_path = self.get_event_folder_path(add_data)
            response = self.move(event_id, new_path[1])
            app.logger.debug(time.strftime("%c") + ": Event move submission by " + username + " " + str(response))

    def _iterate_child_xml(self, child, author):
        try:
            is_published = child.find('last-published-on').text
        except AttributeError:
            is_published = False

        dates = child.findall('event-dates')
        dates_str = []
        dates_html_array = []
        for date in dates:
            try:
                start = date.find('start-date').text.strip()
                end = date.find('end-date').text.strip()

                if start != 'None':
                    start = int(start) / 1000
                if end != 'None':
                    end = int(end) / 1000
            except TypeError:
                all_day = None
                continue
            try:
                all_day = date.find('all-day').text
            except:
                all_day = None
            dates_str.append({
                'start': start,
                'end': end,
            })
            friendly_date = self.convert_timestamps_to_bethel_string(start, end, all_day)
            if friendly_date:
                dates_html_array.append(friendly_date)

        page_values = {
            'author': author,
            'id': child.find('id').text or None,
            'title': child.find('title').text or None,
            'created-on': child.find('created-on').text or None,
            'path': 'https://www.bethel.edu/' + child.find('path').text or None,
            'is_published': is_published,
            'event-dates': dates_str,
            'html': '<br/>'.join(dates_html_array),
            'is_all_day': all_day
        }
        # This is a match, add it to array

        return page_values

    """
    Submitting a new or edited event form combined into one method
    """
    def submit_new_or_edit(self, rform, username, eid, dates, num_dates, metadata_list, wysiwyg_keys, workflow):
        # Changes the dates to a timestamp, needs to occur after a failure is detected or not
        add_data = self.get_add_data(metadata_list, rform, wysiwyg_keys)
        add_data['event-dates'] = self.change_dates(dates)
        if not eid:
            bid = app.config['EVENTS_BASE_ASSET']
            event_data, metadata, structured_data = self.cascade_connector.load_base_asset_by_id(bid, 'page')
            asset = self.update_structure(event_data, metadata, structured_data, add_data, username, num_dates, workflow=workflow)
            resp = self.create_page(asset)
            eid = resp.asset['page']['id']
            self.log_sentry("New event submission", resp)
        else:
            page = self.read_page(eid)
            event_data, metadata, structured_data = page.get_asset()
            asset = self.update_structure(event_data, metadata, structured_data, add_data, username, num_dates, workflow=workflow, event_id=eid)

            self.check_new_year_folder(eid, add_data, username)
            proxy_page = self.read_page(eid)
            resp = proxy_page.edit_asset(asset)
            self.log_sentry("Event edit submission", resp)

        self.cascade_call_logger(locals())
        return add_data, asset, eid

    def get_event_dates(self, form):
        event_dates = []

        num_dates = int(form['num_dates'])
        for i in range(1, num_dates+1):  # the page doesn't use 0-based indexing

            i = str(i)
            new_date = {
                'start_date': form.get('start' + i, ''),
                'end_date': form.get('end' + i, ''),
                'all_day': form.get('allday' + i, ''),
                'outside_of_minnesota': form.get('outsideofminnesota' + i, ''),
                'time_zone': form.get('timezone' + i, ''),
                'no_end_date': form.get('noenddate' + i, '')
            }

            event_dates.append(new_date)

        # convert event dates to JSON
        return event_dates, num_dates

    def check_event_dates(self, event_dates):
        dates_good = True
        for i in range(len(event_dates)):
                                                        # XOR either having an end date or "no end date" checked
            start_and_end = event_dates[i]['start_date'] and \
                                               (bool(event_dates[i]['end_date']) != bool(event_dates[i]['no_end_date']))

            time_zone_check = True
            if event_dates[i]['outside_of_minnesota'] and str(event_dates[i]['time_zone']) == '':
                time_zone_check = False

            if not (start_and_end and time_zone_check):
                dates_good = False

            # Because events that don't need an end date don't have one, just set the end to be the same as the start to
            # appease the date parser later.
            if event_dates[i]['no_end_date'] == u'on' and not event_dates[i]['end_date']:
                event_dates[i]['end_date'] = event_dates[i]['start_date']

        return json.dumps(event_dates), dates_good

    def change_dates(self, event_dates):
        for i in range(len(event_dates)):
            # Get rid of the fancy formatting so we just have normal numbers
            start = event_dates[i]['start_date'].split(' ')
            end = event_dates[i]['end_date'].split(' ')
            start[1] = start[1].replace('th', '').replace('st', '').replace('rd', '').replace('nd', '')
            end[1] = end[1].replace('th', '').replace('st', '').replace('rd', '').replace('nd', '')

            start = " ".join(start)
            end = " ".join(end)

            event_dates[i]['start_date'] = start
            event_dates[i]['end_date'] = end

            # Convert to a unix timestamp, and then multiply by 1000 because Cascade uses Java dates
            # which use milliseconds instead of seconds
            try:
                event_dates[i]['start_date'] = self.date_str_to_timestamp(event_dates[i]['start_date'])
            except ValueError as e:
                app.logger.error(time.strftime("%c") + ": error converting start date " + str(e))
                event_dates[i]['start_date'] = None
            try:
                event_dates[i]['end_date'] = self.date_str_to_timestamp(event_dates[i]['end_date'])
            except ValueError as e:
                app.logger.error(time.strftime("%c") + ": error converting end date " + str(e))
                event_dates[i]['end_date'] = None

            # As long as the value for these checkboxes are NOT '' or 'False'
            # the value in event_dates will be set to 'Yes'
            if event_dates[i]['all_day']:
                event_dates[i]['all_day'] = 'Yes'
            else:
                event_dates[i]['all_day'] = 'No'
            if event_dates[i]['outside_of_minnesota']:
                event_dates[i]['outside_of_minnesota'] = 'Yes'
            else:
                event_dates[i]['outside_of_minnesota'] = 'No'

        return event_dates

    def validate_form(self, rform, dates_good, dates):

        from forms import EventForm
        form = EventForm()

        if not form.validate_on_submit() or not dates_good:
            if 'event_id' in rform.keys():
                event_id = rform['event_id']
            else:
                new_form = True
            author = rform["author"]
            num_dates = int(rform['num_dates'])

            return render_template('event-form.html', **locals())

    def build_edit_form(self, event_id):
        page = self.read_page(event_id)
        multiple = ['event-dates']
        edit_data = self.get_edit_data(page.get_structured_data(), page.get_metadata(), multiple)
        # set dates and return for use in form
        # convert dates to json so we can use Javascript to create custom DateTime fields on the form
        dates = self.sanitize_dates(edit_data['event-dates'])
        dates = fjson.dumps(dates)

        author = edit_data['author']

        return edit_data, dates, author

    def date_str_to_timestamp(self, date):
        try:
            return int(datetime.datetime.strptime(date, '%B %d  %Y, %I:%M %p').strftime("%s")) * 1000
        except TypeError:
            return None

    def timestamp_to_date_str(self, timestamp_date):
        try:
            return datetime.datetime.fromtimestamp(int(timestamp_date) / 1000).strftime('%B %d  %Y, %I:%M %p')
        except TypeError:
            return None

    def update_structure(self, event_data, metadata, structured_data, add_data, username, num_dates, workflow=None, event_id=None):
        """
         Could this be cleaned up at all?
        """
        new_data = {}
        for key in add_data:
            try:
                # Changes date's value names to be hyphens
                if key == 'event-dates':
                    new_data[key.replace('_', '-')] = add_data[key]
                    for i in range(0, num_dates):
                        # The temp dict is made to later replace new_data's dict
                        temp_data = {
                            'start-date': None,
                            'end-date': None,
                            'all-day': None,
                            'outside-of-minnesota': None,
                            'time-zone': None,
                            'no-end-date': None
                        }
                        for val in add_data[key][i]:
                            temp_data[val.replace('_', '-')] = add_data['event-dates'][i][val]
                        new_data[key.replace('_', '-')][i] = temp_data
                else:
                    new_data[key.replace('_', '-')] = add_data[key]
            except:
                pass

        # put it all into the final asset with the rest of the SOAP structure
        hide_site_nav, parent_folder_path = self.get_event_folder_path(new_data)

        new_data['parentFolderID'] = ''
        new_data['parentFolderPath'] = parent_folder_path

        new_data['hide-site-nav'] = [hide_site_nav]
        new_data['tinker-edits'] = 1

        # allows for multiple authors. If none set, default to username
        if 'author' not in new_data or new_data['author'] == "":
            new_data['author'] = username

        self.update_asset(event_data, new_data)

        self.add_workflow_to_asset(workflow, event_data)

        if event_id:
            new_data['id'] = event_id

        return event_data

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

        if app.config['UNIT_TESTING']:
            path = "/_testing/philip-gibbens/events-tests"

        self.copy(app.config['BASE_ASSET_EVENT_FOLDER'], path, 'folder')

        return hide_site_nav, path

    def get_current_year_folder(self, event_id):
        # read in te page and find the current year
        page_asset = self.read(event_id, 'page')
        path = find(page_asset, 'path', False)
        # path = asset['asset']['page']['path']
        try:
            year = re.search('events/(\d{4})/', path).group(1)
            return int(year)
        except AttributeError:
            return None

    def get_year_folder_value(self, data):
        dates = data['event-dates']

        max_year = 0
        for date in dates:
            date_str = self.timestamp_to_date_str(date['end-date'])
            end_date = datetime.datetime.strptime(date_str, '%B %d  %Y, %I:%M %p').date()
            try:
                year = end_date.year
            except AttributeError:
                # if end_date is none and this fails, revert to current year.
                year = datetime.date.today().year
            if year > max_year:
                max_year = year

        return max_year

    # Converts date dict to the date picker format that front-end tinker can read
    def sanitize_dates(self, dates):
        for date in dates:
            if 'all_day' in date and (date['all_day'] == "::CONTENT-XML-CHECKBOX::No" or date['all_day'] == "::CONTENT-XML-CHECKBOX::"):
                date['all_day'] = None
            if 'outside_of_minnesota' in date and (date['outside_of_minnesota'] == "::CONTENT-XML-CHECKBOX::No" or date['outside_of_minnesota'] == "::CONTENT-XML-CHECKBOX::"):
                date['outside_of_minnesota'] = None
        return dates

    # this callback is used with the /edit_all endpoint. The primary use is to modify all assets
    def edit_all_callback(self, asset_data):
        pass

    # The search method that does the actual searching for the /search in events/init
    def get_search_results(self, selection, title, start, end):
        # Get the events and then split them into user events and other events for quicker searching
        # TODO: this method is returning no results
        events = self.traverse_xml(app.config['EVENTS_XML_URL'], 'event')
        # Quick check with assignment
        if selection and '-'.join(selection) == '1':
            events_to_iterate = events
            # default is for the automatic event population
            forms_header = "All Events"
        else:
            user_events, other_events = self.split_user_events(events)
            if selection and '-'.join(selection) == '2':
                events_to_iterate = user_events
                forms_header = "My Events"
            else:
                events_to_iterate = other_events
                forms_header = "Other Events"
        # Early return if no parameters to check in the search
        if not title and not start and not end:
            return events_to_iterate, forms_header

        # to_return will hold all of the events that match the search criteria
        to_return = []

        # This checks if exactly one date is missing, and ignores if both are present or if both are missing (XOR)
        if (start == 0) != (end == 0):
            # By default, both start/end date values are the midnights at the very beginning of the day, so
            # if start == end, then it won't catch any events. Therefore we add a day onto end if we need to
            if start == 0:
                # This means that they didn't submit a start date, so get the value from end and then add a day to give
                # a full 24-hour window to match events into
                start = end
                end += datetime.timedelta(days=1)
            elif end == 0:
                # This means that they didn't submit an end date, so set end to one day after the start value given
                end = start + datetime.timedelta(days=1)
            # At this point there is now guaranteed both start and end dates

        # Check if they pass in same start/end day, make end 24 hours later to give a range
        if start != 0 and end != 0 and self.compare_datetimes(start, end) == 0:
            end += datetime.timedelta(days=1)

        # At this point both start and end should either both be 0 or both be datetime objects that are not equal

        for event in events_to_iterate:
            check_title = bool(title)
            title_matches = check_title and title.lower() in event['title'].lower()
            check_dates = start != 0 and end != 0 and len(event['event-dates']) > 0
            dates_matched = check_dates and self.event_dates_in_date_range(event['event-dates'], start, end)

            add_event = False
            if check_title and title_matches and check_dates and dates_matched:
                add_event = True
            elif check_title and title_matches and not check_dates:
                add_event = True
            elif check_dates and dates_matched and not check_title:
                add_event = True

            if add_event:
                to_return.append(event)

        return to_return, forms_header

    def event_dates_in_date_range(self, list_of_dates, start, end):
        # Loop through event's dates to see if it matches the queried date range
        for date in list_of_dates:
            try:
                # Form Start/End timestamps converted to datetime and then formatted to match start and end
                event_start = datetime.datetime.fromtimestamp(date['start'])
                event_end = datetime.datetime.fromtimestamp(date['end'])
            except TypeError:
                # This try/catch is only needed because the asset at events/event can't easily be deleted
                # from the Cascade DB
                # TODO: remove the reference in the DB then remove that asset then remove this try/catch
                break

            A = self.compare_datetimes(start, event_start) <= 0  # Search start is before event start
            B = self.compare_datetimes(start, event_start) >= 0  # Search start is after event start
            C = self.compare_datetimes(start, event_end) <= 0    # Search start is before event end
            # D = self.compare_datetimes(start, event_end) >= 0  # Search start is after event end (auto-fail)
            # E = self.compare_datetimes(end, event_start) <= 0  # Search end is before event start (auto-fail)
            F = self.compare_datetimes(end, event_start) >= 0    # Search end is after event start
            G = self.compare_datetimes(end, event_end) <= 0      # Search end is before event end
            H = self.compare_datetimes(end, event_end) >= 0      # Search end is after event end

            if (A or (B and C)) and ((F and G) or H):
                # This is a pretty complicated boolean expression, so I'm going to comment on it for everyone
                # else's sake. There are 4 cases where an event would be added to the list 'to_return':
                # 1. A & H         ==> The search range completely encompasses the event being looked at
                # 2. B & C & F & G ==> The event being looked at completely encompasses the search range
                # 3. B & C & H     ==> The search range starts inside the event being looked at and continues after
                # 4. A & F & G     ==> The search range starts before the event being looked at and ends inside
                # Since any one of those conditions could make this statement true, I wrote them all together in
                # a large OR statement. I then reverse-FOIL'd to reduce it down to the boolean expression
                # used in the if statement above.

                # Return immediately on first match to save time
                return True
        # Means that none of the dates in list_of_dates overlapped the queried date range
        return False

    def compare_datetimes(self, a, b):
        zero = datetime.timedelta(seconds=0)
        # If a is before b, return -1
        if (b-a) > zero:
            return -1
        # If a is after b, return 1
        elif (b-a) < zero:
            return 1
        # If a and b have the same value, return 0
        else:
            return 0

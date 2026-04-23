# Global
import datetime
import json
import re
import time

# Packages
from bu_cascade.asset_tools import find, convert_asset
from flask import session
from flask import json as fjson

# Local
from tinker import app
from tinker.tinker_controller import TinkerController


class EventsController(TinkerController):
    # find_all is currently unused for events (but used for the e-annz)
    def inspect_child(self, child, find_all=False, csv=False):
        try:
            author = child.find('author').text
            author = author.replace(' ', '').split(',')
        except AttributeError:
            author = []
        if author == []:
            author = child.find('created-by').text
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

        if (author is not None and username in author) or 'Event Approver' in session['groups'] or (
            school_event and school_event != 'None'):
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
            'title': child.find('title').text.replace(' - - ', '--') or None,
            'created-on': child.find('created-on').text or None,
            'path': 'https://www.bethel.edu/' + child.find('path').text.replace(' - - ', '--') or None,
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

    def submit_new_or_edit(self, rform, username, eid, metadata_list):
        # Changes the dates to a timestamp, needs to occur after a failure is detected or not
        add_data = self.get_add_data(metadata_list, rform)

        add_data['off-campus-location'] = add_data['off-campus-location'][0] if 'off-campus-location' in add_data else {}
        add_data['event-dates'] = self.change_dates(add_data['event-dates']) if 'event-dates' in add_data else []

        if not eid:
            asset = self.update_structure(add_data, username)

            workflow = self.create_workflow(app.config['EVENTS_WORKFLOW_ID'], session['username'] + '--' + rform['title'] + ', ' + datetime.datetime.now().strftime("%m/%d/%Y %I:%M %p"))
            self.add_workflow_to_asset(workflow, asset)
            
            resp = self.create_page(asset)
            eid = resp.asset['page']['id']
            self.log_sentry("New event submission", "createdAssetId = " + eid)
        else:
            asset = self.update_structure(add_data, username, event_id=eid)

            self.check_new_year_folder(eid, add_data, username)
            proxy_page = self.read_page(eid)
            resp = proxy_page.edit_asset(asset)
            self.log_sentry("Event edit submission", resp)

        self.cascade_call_logger(locals())
        return add_data, asset, eid

    def get_event_dates(self, form):
        event_dates = []

        num_dates = int(form['num_dates'])
        for i in range(1, num_dates + 1):  # the page doesn't use 0-based indexing
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
            start = event_dates[i]['start-date'].split(' ')
            start[1] = start[1].replace('th', '').replace('st', '').replace('rd', '').replace('nd', '').replace('.', '')

            if event_dates[i]['end-date']:
                end = event_dates[i]['end-date'].split(' ')
                end[1] = end[1].replace('th', '').replace('st', '').replace('rd', '').replace('nd', '').replace('.', '')
            else:
                event_dates[i]['end-date'] = None

            start = " ".join(start)
            end = " ".join(end)

            event_dates[i]['start-date'] = start
            event_dates[i]['end-date'] = end

            # Convert to a unix timestamp, and then multiply by 1000 because Cascade uses Java dates
            # which use milliseconds instead of seconds
            try:
                event_dates[i]['start-date'] = self.date_str_to_timestamp(event_dates[i]['start-date'])
            except ValueError as e:
                app.logger.error(time.strftime("%c") + ": error converting start date " + str(e))
                event_dates[i]['start-date'] = None

            if event_dates[i]['end-date']:
                try:
                    event_dates[i]['end-date'] = self.date_str_to_timestamp(event_dates[i]['end-date'])
                except ValueError as e:
                    app.logger.error(time.strftime("%c") + ": error converting end date " + str(e))
                    event_dates[i]['end-date'] = None

            # As long as the value for these checkboxes are NOT '' or 'False'
            # the value in event_dates will be set to 'Yes'
            # if event_dates[i].get('all-day'):
            #     event_dates[i]['all-day'] = 'Yes'
            # else:
            #     event_dates[i]['all-day'] = 'No'
            # if event_dates[i].get('outside-of-minnesota'):
            #     event_dates[i]['outside-of-minnesota'] = 'Yes'
            # else:
            #     event_dates[i]['outside-of-minnesota'] = 'No'

        return event_dates

    def validate_form(self, rform):
        from tinker.events.forms import get_event_form
        form = get_event_form(**rform)

        # Validate fieldset fields
        fieldset_errors = {}
        for field in form:
            if not field.name in rform:
                form[field.name].validators = []
            if field.type == 'FieldsetField':
                data = field.data
                for f in field.fields:
                    if data:
                        for obj in data:
                            if f.name in obj:
                                f.data = obj[f.name]
                                for validator in f.validators:
                                    try:
                                        class_name = getattr(validator, '__class__', None).__name__
                                        if class_name == 'InputRequired':
                                            continue
                                        elif class_name == 'DataRequired':
                                            if f.data is None or f.data == '':
                                                raise ValueError(f"{f.label.text} is required.")
                                        validator(form, f)
                                    except Exception as e:
                                        if f.name not in fieldset_errors:
                                            fieldset_errors[f.name] = []
                                        fieldset_errors[f.name].append(str(e))

        # Validate the form as a whole
        valid = form.validate_on_submit()
        if not valid:
            errors = form.errors
            print(errors)

        return form, fieldset_errors, valid

    def build_edit_form(self, event_id):
        page = self.read_page(event_id)
        multiple = ['event_dates', 'cost']
        edit_data = self.get_edit_data(page.get_structured_data(), page.get_metadata(), multiple)
        # set dates and return for use in form
        # convert dates to json so we can use Javascript to create custom DateTime fields on the form
        dates = self.sanitize_dates(edit_data['event_dates'])
        dates = fjson.dumps(dates)

        return convert_asset(edit_data), dates

    def date_str_to_timestamp(self, date_string):
        try:
            return int(datetime.datetime.strptime(date_string, '%B %d %Y, %I:%M %p').strftime("%s")) * 1000
        except TypeError:
            return None

    def timestamp_to_date_str(self, timestamp_date):
        try:
            return datetime.datetime.fromtimestamp(int(timestamp_date) / 1000).strftime('%B %d %Y, %I:%M %p')
        except TypeError:
            return None

    def update_structure(self, add_data, username, event_id=None):
        bid = app.config['EVENTS_BASE_ASSET']
        event_data, metadata, structured_data = self.cascade_connector.load_base_asset_by_id(bid, 'page')

        # put it all into the final asset with the rest of the SOAP structure
        hide_site_nav, parent_folder_path = self.get_event_folder_path(add_data)

        add_data['parentFolderID'] = ''
        add_data['parentFolderPath'] = parent_folder_path

        add_data['hide-site-nav'] = [hide_site_nav]
        add_data['tinker-edits'] = 1

        if event_id:
            add_data['id'] = event_id
            # delete author, as we don't want it to change. But, it gets set in get_add_data()
            add_data.pop('author', None)
        else:
            add_data['author'] = username

        self.update_asset(event_data, add_data)

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

        elif common_elements(['Johnson Gallery', 'Olson Gallery', 'Art Galleries'], general):
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
            year = re.search('events/.*(\d{4})/', path).group(1)
            return int(year)
        except AttributeError:
            return None

    def get_year_folder_value(self, data):
        dates = data['event-dates']

        max_year = 0
        for date in dates:
            date_str = self.timestamp_to_date_str(date['end-date'])
            try:
                end_date = datetime.datetime.strptime(date_str, '%B %d %Y, %I:%M %p').date()
                year = end_date.year
            except Exception:
                # if end_date is none and this fails, revert to current year.
                year = datetime.date.today().year
            if year > max_year:
                max_year = year

        return max_year

    # Converts date dict to the date picker format that front-end tinker can read
    def sanitize_dates(self, dates):
        for date in dates:
            if 'all_day' in date and (
                    date['all_day'] == "::CONTENT-XML-CHECKBOX::No" or date['all_day'] == "::CONTENT-XML-CHECKBOX::"):
                date['all_day'] = None
            if 'outside_of_minnesota' in date and (date['outside_of_minnesota'] == "::CONTENT-XML-CHECKBOX::No" or date[
                'outside_of_minnesota'] == "::CONTENT-XML-CHECKBOX::"):
                date['outside_of_minnesota'] = None
        return dates

    # this callback is used with the /edit_all endpoint. The primary use is to modify all assets
    def edit_all_callback(self, asset_data):
        pass

    # The search method that does the actual searching for the /search in events/init
    def get_search_results(self, selection, title, start, end):
        # Get the events and then split them into user events and other events for quicker searching
        events = self.traverse_xml(app.config['EVENTS_XML_URL'], 'event')
        # Quick check with assignment
        if selection and '-'.join(selection) == '2':
            events_to_iterate = events
            # default is for the automatic event population
            forms_header = "All Events"
        else:
            user_events, other_events = self.split_user_events(events)
            if selection and '-'.join(selection) == '1':
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

        # Check if they pass in same start/end day, make end 24 hours later to give a range
        if start != 0 and end != 0 and self.compare_datetimes(start, end) == 0:
            end += datetime.timedelta(days=1)

        for event in events_to_iterate:
            title_matches = title and title.lower() in event['title'].lower()
            check_dates = (start != 0 or end != 0) and len(event['event-dates']) > 0
            dates_matched = check_dates and self.event_dates_in_date_range(event['event-dates'], start, end)

            # Title and date fields filled
            if title_matches and check_dates and dates_matched:
                to_return.append(event)
            # Title but no dates
            elif title_matches and not check_dates:
                to_return.append(event)
            # Dates but no title
            elif check_dates and dates_matched and not title:
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

            if start != 0:
                searchstart_before_eventstart = self.compare_datetimes(start, event_start) <= 0  # Search start is before event start
                searchstart_after_eventstart = self.compare_datetimes(start, event_start) >= 0  # Search start is after event start
                searchstart_before_eventend = self.compare_datetimes(start, event_end) <= 0  # Search start is before event end
                start_params = (searchstart_before_eventstart or searchstart_after_eventstart) and searchstart_before_eventend
            else:
                start_params = True

            if end != 0:
                searchend_after_eventstart = self.compare_datetimes(end, event_start) >= 0  # Search end is after event start
                searchend_before_eventend = self.compare_datetimes(end, event_end) <= 0  # Search end is before event end
                searchend_after_eventend = self.compare_datetimes(end, event_end) >= 0  # Search end is after event end
                end_params = searchend_after_eventstart and (searchend_before_eventend or searchend_after_eventend)
            else:
                end_params = True

            if start_params and end_params:
                # Return immediately on first match to save time
                return True
        # Means that none of the dates in list_of_dates overlapped the queried date range
        return False

    def compare_datetimes(self, a, b):
        zero = datetime.timedelta(seconds=0)
        # If a is before b, return -1
        if (b - a) > zero:
            return -1
        # If a is after b, return 1
        elif (b - a) < zero:
            return 1
        # If a and b have the same value, return 0
        else:
            return 0

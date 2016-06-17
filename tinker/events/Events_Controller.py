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
    def node(self, s_data, edit_data, date_count, dates):
        for node in s_data:
            node_identifier = node.identifier.replace('-', '_')
            node_type = node.type
            if node_type == "text":
                edit_data[node_identifier] = node.text
            elif node_type == 'group':
                # These are the event dates. Create a dict so we can convert to JSON later.
                dates[date_count] = read_date_data_structure(node)
                date_count += 1
            elif node_identifier == 'image':
                edit_data['image'] = node.filePath

    def metadata(self, dynamic_fields, edit_data):
        for field in dynamic_fields:
            # This will fail if no metadata is set. It should be required but just in case
            if field.fieldValues:
                items = [item.value for item in field.fieldValues.fieldValue]
                edit_data[field.name.replace('-', '_')] = items

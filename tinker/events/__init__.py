# Global
import datetime
import json
import re
import time

# Packages
from bu_cascade.asset_tools import update, convert_asset
from flask import redirect, session, render_template, request, url_for, jsonify
from flask_classy import FlaskView, route
from collections import OrderedDict
from werkzeug.datastructures import MultiDict

# Local
from tinker import app, cache
from tinker.events.events_controller import EventsController


class EventsView(FlaskView):
    route_base = '/events'
    _multiple_segment_pattern = re.compile(r'^\[multiple\]([^_]+)_(\d+)$')

    def __init__(self):
        self.base = EventsController()
        self.base.datetime_format = "%B %d %Y, %I:%M %p"

    # Allows any user to access events
    def before_request(self, name, **kwargs):
        pass

    def index(self):
        username = session['username']

        @cache.memoize(timeout=300)
        def index_cache(username):
            show_create = True
            if 'Tinker Events - CAS' in session['groups'] or 'Event Approver' in session['groups']:
                # The special admin view
                all_schools = OrderedDict({
                    1: 'My Events',
                    2: 'All Events',
                    3: 'Other Events'},
                    key=lambda t: t[0]
                )
            else:
                all_schools = OrderedDict({
                    1: 'User Events'}
                )

            return render_template('events/home.html', show_create=show_create, all_schools=all_schools, list_of_events=None,
                                   formsHeader="All Events")

        return index_cache(username)

    def confirm(self):
        return render_template('events/submit-confirm.html', **locals())

    def event_in_workflow(self):
        return render_template('events/in-workflow.html')

    def _get_multiple_segments(self, key):
        segments = []
        for part in (key or '').split('__'):
            match = self._multiple_segment_pattern.match(part)
            if not match:
                continue
            segments.append((match.group(1), int(match.group(2)), part))
        return segments

    def _normalize_group_name_segments(self, group_name):
        if not group_name:
            return []

        if '__' in group_name:
            raw_parts = group_name.split('__')
        else:
            # group_name from button classes uses '_' between nested [multiple] segments.
            raw_parts = re.split(r'_(?=\[multiple\])', group_name)

        return [
            part for part in raw_parts
            if self._multiple_segment_pattern.match(part)
        ]

    def _multiple_count_key(self, parent_instances, base_key):
        if parent_instances:
            return '__'.join(parent_instances + [base_key])
        return base_key

    def _build_multiples_from_form(self, rform):
        multiples = {}
        for key in rform.keys():
            parent_instances = []
            for base_key, index, concrete_identifier in self._get_multiple_segments(key):
                count_key = self._multiple_count_key(parent_instances, base_key)
                if count_key not in multiples or index > multiples[count_key]:
                    multiples[count_key] = index
                parent_instances.append(concrete_identifier)
        return multiples

    def _remove_multiple_from_form(self, rform, group_name):
        target_segments = self._normalize_group_name_segments(group_name)
        if not target_segments:
            return MultiDict(rform)

        target_parent = target_segments[:-1]
        target_match = self._multiple_segment_pattern.match(target_segments[-1])
        if not target_match:
            return MultiDict(rform)

        target_base = target_match.group(1)
        remove_index = int(target_match.group(2))

        updated_form = MultiDict()
        for key in rform.keys():
            values = rform.getlist(key)
            parts = key.split('__')
            segment_positions = []
            for idx, part in enumerate(parts):
                match = self._multiple_segment_pattern.match(part)
                if match:
                    segment_positions.append((idx, part, match.group(1), int(match.group(2))))

            new_key = key
            if len(segment_positions) > len(target_parent):
                current_parent = [segment[1] for segment in segment_positions[:len(target_parent)]]
                if current_parent == target_parent:
                    target_segment = segment_positions[len(target_parent)]
                    segment_idx = target_segment[3]
                    segment_base = target_segment[2]

                    if segment_base == target_base:
                        if segment_idx == remove_index:
                            continue
                        if segment_idx > remove_index:
                            parts[target_segment[0]] = '[multiple]' + segment_base + '_' + str(segment_idx - 1)
                            new_key = '__'.join(parts)

            for value in values:
                updated_form.add(new_key, value)

        return updated_form

    # CANT CACHE THIS
    def add(self):

        # temp deal with ITS-216352
        # if a request came to /e-announcments/new/ or /events/add/ directly, go to the homepage first to prevent
        # the CAS issue. short term fix, todo find long term issue (probably with mod_auth_cas

        # 9/21/20 update, adding some extra sentry logging to try and further debug. The redirect isn't always working.
        if not session.get('username'):
            resp = None
            kwargs = {
                'referrer': request.referrer,
                'request': request,
                'username': session.get('username')
            }
            self.base.log_sentry('Loading Events without Username', resp, **kwargs)
            return redirect(url_for('EventsView:index'))
        else:
            resp = None
            kwargs = {
                'referrer': request.referrer,
                'request': request,
                'username': session.get('username')
            }
            self.base.log_sentry('Loading Events with Username', resp, **kwargs)

        # import this here so we dont load all the content from cascade during homepage load
        from tinker.events.forms import get_event_form

        form = get_event_form()
        return render_template('events/form.html', form=form, new_form=True)

    def edit(self, event_id):
        # if the event is in a workflow currently, don't allow them to edit. Instead, redirect them.
        if self.base.asset_in_workflow(event_id, asset_type='page'):
            return redirect(url_for('EventsView:event_in_workflow'), code=302)

        edit_data, dates, multiples = self.base.build_edit_form(event_id)
        # todo: fix this with the submit_all() functionality ASK CALEB
        # convert 'On/Off campus' to 'On/Off Campus' for all events
        from tinker.events.forms import get_event_form
        form = get_event_form(multiples=multiples, cascade_data=edit_data)
        # if 'location' in edit_data and edit_data['location']:
        #     edit_data['location'].replace(' c', ' C')

        return render_template('events/form.html', **locals())

    def duplicate(self, event_id):
        edit_data, dates, multiples = self.base.build_edit_form(event_id)
        from tinker.events.forms import get_event_form
        form = get_event_form(multiples=multiples, cascade_data=edit_data)
        new_form = True

        return render_template('events/form.html', **locals())

    @route("/api/add-multiple", methods=['POST'])
    def add_multiple(self):
        from tinker.events.forms import get_event_form

        rform = request.form
        multiples = self._build_multiples_from_form(rform)

        group_name = rform.get('group_name', '')
        group_segments = self._normalize_group_name_segments(group_name)
        if group_segments:
            group_match = self._multiple_segment_pattern.match(group_segments[-1])
            if group_match:
                parent_instances = group_segments[:-1]
                base_key = group_match.group(1)
                index = int(group_match.group(2))
                count_key = self._multiple_count_key(parent_instances, base_key)
                current_count = multiples.get(count_key, index)
                multiples[count_key] = max(current_count, index) + 1

        form = get_event_form(multiples=multiples)
        form.process(formdata=rform)

        event_id = rform.get('event_id')
        html = render_template('events/form_fields.html', form=form, event_id=event_id)
        return jsonify({'html': html})

    @route("/api/remove-multiple", methods=['POST'])
    def remove_multiple(self):
        from tinker.events.forms import get_event_form

        rform = self._remove_multiple_from_form(request.form, request.form.get('group_name', ''))
        multiples = self._build_multiples_from_form(rform)

        form = get_event_form(multiples=multiples)
        form.process(formdata=rform)

        event_id = rform.get('event_id')
        html = render_template('events/form_fields.html', form=form, event_id=event_id)
        return jsonify({'html': html})

    @route("/submit", methods=['post'])
    def submit(self):

        rform = request.form
        eid = rform.get('event_id')

        multiples = self._build_multiples_from_form(rform)
        form, passed = self.base.validate_form(multiples=multiples)

        if not passed:
            if eid:
                form.data['event_id'] = eid
                event_id = eid
            else:
                new_form = True

            return render_template('events/form.html', **locals())

        form.process(formdata=rform, data=None, obj=None, **request.files)
        add_data, asset, eid = self.base.submit_new_or_edit(form)

        # todo: Test this
        if 'link' in add_data and add_data['link']:
            from tinker.admin.redirects import RedirectsView
            view = RedirectsView()
            path = str(asset['page']['parentFolderPath'] + "/" + asset['page']['name'])
            view.new_internal_redirect_submit(path, add_data['link'])

        return render_template("events/submit-confirm.html", **locals())

    @route('/api/reset-tinker-edits/<event_id>', methods=['get', 'post'])
    def reset_tinker_edits(self, event_id):
        my_page = self.base.read_page(event_id)

        asset, md, sd = my_page.get_asset()
        update(md, 'tinker-edits', '0')
        my_page.edit_asset(asset)

        return event_id

    def edit_all(self):
        type_to_find = 'system-page'
        xml_url = app.config['EVENTS_XML_URL']
        self.base.edit_all(type_to_find, xml_url)
        return 'success'

    # This endpoint is being re-added so that unit tests will be self-deleting. This endpoint is publicly visible, but
    # it is not referenced anywhere on any page, so the public shouldn't know of its existence.
    # Todo: this should require auth! otherwise, anyone could delete any event
    @route("/delete/<event_id>", methods=['GET'])
    def delete(self, event_id):
        event_page = self.base.read_page(event_id)
        response = event_page.delete_asset()
        self.base.cascade_call_logger(locals())
        self.base.unpublish(event_id, 'page')
        app.logger.debug(time.strftime("%c") + ": Event deleted by " + session['username'] + " " + str(response))
        self.base.publish(app.config['EVENT_XML_ID'])
        return render_template('events/delete-confirm.html')

    # This is the search for events to pare down what is being shown
    @route("/search", methods=['POST'])
    def search(self):
        # Load the data, get the event type selection and title of the event the user is searching for
        data = json.loads(request.data)
        selection = data['selection']
        title = data['title']
        try:
            start = datetime.datetime.strptime(data['start'], "%a %b %d %Y")
        except:
            start = 0
        try:
            end = datetime.datetime.strptime(data['end'], "%a %b %d %Y")
        except:
            end = 0

        search_results, forms_header = self.base.get_search_results(selection, title, start, end)
        search_results.sort(key=lambda event: event['event-dates'][0]['start'], reverse=False)
        return render_template('events/search-results.html', list_of_events=search_results, formsHeader=forms_header)

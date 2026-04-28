# coding: utf-8
"""
Event form — built dynamically from the Cascade data definition.

The only fields that are NOT sourced from the data definition are Cascade page
metadata fields (title, metaDescription, link, image) and the category
SelectMultipleFields (from the /Event metadataset).  Every structured-data
field is created by walking the parsed data definition tree.

Field-naming conventions (must match bu_cascade get_add_data / get_edit_data):
  - Top-level text/asset:   <identifier>          e.g. guestInstructions
  - Group child (flat):     <group>_<child>        e.g. date_eventStart
  - Repeating group child:  <group>_<child>[]      handled via FieldsetField
  - Nested group:           <outer>_<inner>_<child>
"""

# Packages
import json

from flask import current_app, request, session
from flask_wtf import FlaskForm
from wtforms import (HiddenField, StringField)
from wtforms.validators import ValidationError, URL

# Shared Cascade form helpers (classes / functions that are not event-specific)
from tinker.cascade_form_helpers import (FieldsetField, _fields_from_def, bind_fields, _flatten_cascade_data,
                                          get_metadata_fields, build_metadata_custom_fields,
                                          get_structured_data_labels)

# Local
from tinker.tinker_controller import TinkerController
from tinker import app
from tinker.data_definition_parser import get_field_definitions


tinker = TinkerController()


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

def length_checker(form, field):
    for word in field.data.split(' '):
        if len(word) > 15:
            raise ValidationError('Words in the title must be 15 characters or less')


def validate_numeric(form, field):
    if not field.data:
        return
    try:
        float(field.data)
    except ValueError:
        raise ValidationError('All Cost fields must be numeric values.')


# ---------------------------------------------------------------------------
# Event-specific field configuration
# ---------------------------------------------------------------------------

# Per-identifier extra config passed to _build_field / _fields_from_def.
# Keys are bare identifiers (no group prefix).  This is the ONLY place
# event-specific knowledge about individual fields lives.
_FIELD_EXTRA = {
    # Date sync — keeps eventEnd >= eventStart
    'eventStart':      {'render_kw': {'onchange': 'syncDates(this)'}},
    'eventEnd':        {'render_kw': {'onchange': 'syncDates(this)'}},
    # All-day event — zeros out time on both date fields
    'hideTime':        {'render_kw': {'onclick': 'setAllDayTime(this)'}},
    # URL validators
    'url':             {'extra_validators': [URL(require_tld=True,
                                                 message='Please enter a valid URL.')]},
    # Cost
    'price':           {'extra_validators': [validate_numeric],
                        'render_kw': {'onblur': 'stripCostChars(this)'}},
    # Registration
    'ticketingURL':    {'extra_validators': [URL(require_tld=True,
                                                 message='Please enter a valid URL.')]},
}


# ---------------------------------------------------------------------------
# Form factory
# ---------------------------------------------------------------------------

def _translate_fieldset_formdata():
    """
    Translate fieldset-namespaced request.form/files keys to plain WTForms
    field names so that field lookups succeed.

    The template renders inputs as  'foo_fieldset::bar[]'  but WTForms calls
    formdata.getlist('bar').  Strip the 'foo_fieldset::' prefix and trailing
    '[]' so every field name resolves correctly.

    Returns a CombinedMultiDict that also includes translated file keys so
    that FileField instances receive their uploaded files.
    """
    from werkzeug.datastructures import MultiDict, CombinedMultiDict

    def _plain(key):
        return key.split('::', 1)[1].rstrip('[]') if '::' in key else key

    form_md = MultiDict()
    for key in request.form.keys():
        for val in request.form.getlist(key):
            form_md.add(_plain(key), val)

    files_md = MultiDict()
    for key in request.files.keys():
        for f in request.files.getlist(key):
            files_md.add(_plain(key), f)

    return CombinedMultiDict([files_md, form_md])


def _assemble_repeating_fieldset_data(field):
    """
    Reconstruct list-of-dicts data for a repeating FieldsetField from the
    raw (un-translated) request.form.

    Flat sub-fields are submitted as:
        {field.name}_fieldset::{sub_field_name}[]  (one value per outer row)

    Nested repeating sub-groups (e.g. timeDescription inside scheduleDetails)
    are submitted with a row-indexed prefix set by the JS updateFieldsets:
        {nested_field.name}_fieldset_{outer_row}::{inner_field_name}[]

    Returns a list of dicts, e.g.:
        [{'date': 'Day 1', 'timeDescription': [{'time': '9am', 'description': '...'}]}, ...]
    or None if no submitted data is found for this group.
    """
    _FSF = FieldsetField

    fieldset_prefix = field.name + '_fieldset'
    sub_fields = field.fields if isinstance(field.fields, list) else list((field.fields or {}).values())

    # Partition sub-fields: flat leaf fields vs. nested repeating groups
    flat_fields = [sf for sf in sub_fields
                   if hasattr(sf, 'name') and not (isinstance(sf, _FSF) and sf.fieldset_type == 'multiple')]
    nested_multiple = [sf for sf in sub_fields
                       if hasattr(sf, 'name') and isinstance(sf, _FSF) and sf.fieldset_type == 'multiple']


    # Collect flat field values for each row, using row-indexed keys
    # e.g. schedule_scheduleDetails_fieldset_1::scheduleDetails_date[]
    #      schedule_scheduleDetails_fieldset_2::scheduleDetails_date[]
    # If not found, fall back to old key (no row index)
    #
    # First, determine num_rows by scanning for keys with row indices
    import re
    # Find all row indices present for this fieldset
    row_index_pattern = re.compile(r'^' + re.escape(fieldset_prefix) + r'_(\d+)::')
    row_indices = set()
    for k in request.form.keys():
        m = row_index_pattern.match(k)
        if m:
            row_indices.add(int(m.group(1)))

    # If no row-indexed keys, fallback to old logic
    if not row_indices:
        raw_map = {}
        for sf in flat_fields:
            raw_key = fieldset_prefix + '::' + sf.name + '[]'
            vals = request.form.getlist(raw_key)
            if vals:
                raw_map[sf.name] = vals
        num_rows = max((len(v) for v in raw_map.values()), default=0)
        if num_rows == 0 and nested_multiple:
            for nsf in nested_multiple:
                row = 1
                while any((nsf.name + '_fieldset_' + str(row) + '::') in k for k in request.form.keys()):
                    row += 1
                num_rows = max(num_rows, row - 1)
        if num_rows == 0:
            return None
        rows = []
        for i in range(num_rows):
            row = {sf_name: raw_map[sf_name][i] if i < len(raw_map[sf_name]) else '' for sf_name in raw_map}
            # Nested groups (legacy fallback)
            for nsf in nested_multiple:
                nested_prefix = nsf.name + '_fieldset_' + str(i + 1)
                nsf_sub = nsf.fields if isinstance(nsf.fields, list) else list((nsf.fields or {}).values())
                nested_raw = {}
                for nf in nsf_sub:
                    if not hasattr(nf, 'name') or isinstance(nf, _FSF):
                        continue
                    nkey = nested_prefix + '::' + nf.name + '[]'
                    vals = request.form.getlist(nkey)
                    if vals:
                        nested_raw[nf.name] = vals
                if nested_raw:
                    nested_num = max(len(v) for v in nested_raw.values())
                    row[nsf.name] = [
                        {nf_name: nested_raw[nf_name][j] if j < len(nested_raw[nf_name]) else ''
                         for nf_name in nested_raw}
                        for j in range(nested_num)
                    ]
            rows.append(row)
        return rows

    # Otherwise, assemble rows by row index
    row_indices = sorted(row_indices)
    rows = []
    for idx in row_indices:
        row = {}
        for sf in flat_fields:
            row_key = f"{fieldset_prefix}_{idx}::{sf.name}[]"
            vals = request.form.getlist(row_key)
            # If multiple values, flatten to first (shouldn't happen for flat fields)
            val = vals[0] if vals else ''
            row[sf.name] = val

        # Assemble nested repeating group data for this specific outer row
        for nsf in nested_multiple:
            nested_prefix = nsf.name + '_fieldset_' + str(idx)
            nsf_sub = nsf.fields if isinstance(nsf.fields, list) else list((nsf.fields or {}).values())
            nested_raw = {}
            for nf in nsf_sub:
                if not hasattr(nf, 'name') or isinstance(nf, _FSF):
                    continue
                nkey = nested_prefix + '::' + nf.name + '[]'
                vals = request.form.getlist(nkey)
                if vals:
                    nested_raw[nf.name] = vals
            if nested_raw:
                nested_num = max(len(v) for v in nested_raw.values())
                row[nsf.name] = [
                    {nf_name: nested_raw[nf_name][j] if j < len(nested_raw[nf_name]) else ''
                     for nf_name in nested_raw}
                    for j in range(nested_num)
                ]
        rows.append(row)
    return rows


def get_event_form(cascade_data=None):
    """
    Build and return an EventForm, optionally pre-populated from raw Cascade
    structured data (the dict returned by get_edit_data).

    cascade_data -- dict from get_edit_data() containing structured-data and
                    metadata fields.  Structured-data fields are flattened
                    using the live data definition so that any data definition
                    file works automatically.  Metadata / fixed fields (title,
                    metaDescription, category lists, etc.) that are NOT
                    identifiers in the data definition pass through unchanged.
    """
    form_kwargs = {}
    if cascade_data:
        field_defs = get_field_definitions(app.config.get('EVENTS_DATA_DEF_ID', ''))
        dd_top_identifiers = {fd['identifier'] for fd in field_defs}
        # Flatten structured-data fields using the data definition
        form_kwargs = _flatten_cascade_data(cascade_data, field_defs)
        # Pass through metadata / fixed fields not covered by the data def
        for key, val in cascade_data.items():
            if key not in dd_top_identifiers:
                form_kwargs[key] = val
        form = _build_event_form_class()(**form_kwargs)
    else:
        # On POST, request.form keys are namespaced ('foo_fieldset::bar[]').
        # Translate them to plain field names so WTForms lookups succeed.
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            form_data = _translate_fieldset_formdata()
            form = _build_event_form_class(validate=True)(formdata=form_data)
        else:
            form = _build_event_form_class()()


    for field in form:
        if isinstance(field, FieldsetField):
            # if field.child_names:
            #     # Single card group: wire the already-bound child fields from the
            #     # form into the card so the template can render them grouped.
            #     field.fields = [form._fields[n] for n in field.child_names
            #                      if n in form._fields]
            #     if form_kwargs:
            #         pfx = field.name + '_'
            #         field.data = {k: v for k, v in form_kwargs.items()
            #                       if k.startswith(pfx)}
            #     elif request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            #         # Assemble any nested repeating groups (e.g. cost_offer inside cost)
            #         for child in field.fields:
            #             if (isinstance(child, FieldsetField)
            #                     and child.fieldset_type == 'multiple'
            #                     and not child.data):
            #                 assembled = _assemble_repeating_fieldset_data(child)
            #                 if assembled is not None:
            #                     child.data = assembled
            # else:
            # Repeating group: bind inner fields and restore pre-populated data.
            bind_fields(form, field.fields, field.name)
            if field.name in form_kwargs:
                field.data = form_kwargs[field.name]
            elif request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
                assembled = _assemble_repeating_fieldset_data(field)
                if assembled is not None:
                    field.data = assembled

    def _json_default(obj):
        from werkzeug.datastructures import FileStorage
        if isinstance(obj, FileStorage):
            return obj.filename
        return str(obj)
    current_app.logger.debug('form.data: %s', json.dumps(form.data, default=_json_default))

    return form


# ---------------------------------------------------------------------------
# EventForm
#
# Fields derived from the data definition are injected into the class dict
# before the class is defined using type().  This means the class body only
# contains the fixed Cascade metadata fields.
# ---------------------------------------------------------------------------

def _build_event_form_class(validate=False):
    """
    Build and return the EventForm class with all data-definition fields
    injected alongside the fixed Cascade metadata fields.
    """

    all_fields = {}

    built_in_fields, _raw_custom_fields = get_metadata_fields(tinker, '/Event-v4')
    on_campus_locations = get_structured_data_labels(tinker, app.config.get('EVENTS_ON_CAMPUS_LOCATIONS_DD_ID', ''))

    # Mark auto-generated top fields as card children of event_basics
    for field in built_in_fields.values():
        rk = dict(field.kwargs.get('render_kw', {}))
        field.kwargs['render_kw'] = rk

    # Ensure 'title' (if present) is the very first child field on the form.
    # Also add the length checker to the title field
    if 'title' in built_in_fields:
        built_in_fields = {'title': built_in_fields.pop('title'), **built_in_fields}
        built_in_fields['title'].kwargs['validators'].append(length_checker)

    # Add built_in_fields as visible children of the FieldsetField
    if not validate:
        top_fields = {
            'event_basics': FieldsetField(
                label='Event basics',
                fieldset_type='single',
                fields=built_in_fields,
            ),
        }
    else:
        top_fields = built_in_fields
    all_fields.update(top_fields)

    # Add built_in_fields as individual HiddenFields (with same names, but hidden)
    from wtforms import HiddenField
    for name in built_in_fields:
        all_fields[f'_hidden_{name}'] = HiddenField()

    # Walk the full data definition tree
    # Pass event-specific field config and choice overrides to the generic helper.
    dd_fields = _fields_from_def(
        get_field_definitions(app.config.get('EVENTS_DATA_DEF_ID', '')),
        field_extra=_FIELD_EXTRA,
        override_choices={'location': on_campus_locations},
    )
    all_fields.update(dd_fields)

    # Remove this?
    # External Link field (only editable by Event Approvers; not in the metadataset)
    if 'Event Approver' in session.get('groups', []):
        link_field = StringField(
            'External Link',
            description="This field only seen by 'Event Approvers'. "
                        "An external link will redirect this event to the external link url.",
        )
    else:
        link_field = HiddenField('External Link')
    all_fields['link'] = link_field

    # Finally, build custom fields from the metadata set
    custom_fields = build_metadata_custom_fields(_raw_custom_fields)
    all_fields.update(custom_fields)

    # Build the class dynamically so WTForms metaclass processes all fields
    return type('EventForm', (FlaskForm,), all_fields)

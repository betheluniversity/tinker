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
  - Nested group:           <outer>_<inner>_<child>
"""

# Packages
import json

from flask import current_app, request, session
from flask_wtf import FlaskForm
from wtforms import (HiddenField, StringField)
from wtforms.validators import ValidationError, URL

from tinker.cascade_form_helpers import (_fields_from_def,
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
# This is the ONLY place event-specific knowledge about individual fields lives.
_FIELD_EXTRA = {
    # Group built-in fields visually in the template as 'Event basics', and specify order.
    # We use lists for 'groups' and 'group_labels' to support the recursive card rendering logic.
    'title': {'render_kw': {'groups': ['event_basics'], 'group_labels': ['Event basics']}, 'order': 0, 'extra_validators': [length_checker]},
    'teaser': {'render_kw': {'groups': ['event_basics'], 'group_labels': ['Event basics']}, 'order': 1},
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

def get_event_form():
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
    form = _build_event_form_class()()

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

def _build_event_form_class():
    """
    Build and return the EventForm class with all data-definition fields
    injected alongside the fixed Cascade metadata fields.
    """

    all_fields = {}
    built_in_fields, _raw_custom_fields = get_metadata_fields(tinker, '/Event-v4')

    all_fields.update(built_in_fields)

    # Walk the full data definition tree
    # Pass event-specific field config and choice overrides to the generic helper.
    on_campus_locations = get_structured_data_labels(tinker, app.config.get('EVENTS_ON_CAMPUS_LOCATIONS_DD_ID', ''))
    dd_fields = _fields_from_def(
        get_field_definitions(app.config.get('EVENTS_DATA_DEF_ID', '')),
        field_extra=_FIELD_EXTRA,
        override_choices={'location': on_campus_locations},
    )
    all_fields.update(dd_fields)

    # Remove this?
    # External Link field (only editable by Event Approvers; not in the metadataset)
    # if 'Event Approver' in session.get('groups', []):
    #     link_field = StringField(
    #         'External Link',
    #         description="This field only seen by 'Event Approvers'. "
    #                     "An external link will redirect this event to the external link url.",
    #     )
    # else:
    #     link_field = HiddenField('External Link')
    # all_fields['link'] = link_field

    # Finally, build custom fields from the metadata set
    custom_fields = build_metadata_custom_fields(_raw_custom_fields)
    all_fields.update(custom_fields)

    # Apply _FIELD_EXTRA and ensure 'order' exists for all fields to support template sorting.
    for name, field in all_fields.items():
        extra = _FIELD_EXTRA.get(name, {})
        rk = dict(field.kwargs.get('render_kw', {}) or {})

        if 'render_kw' in extra:
            rk.update(extra['render_kw'])

        # Ensure 'order' is always present in render_kw for the Jinja sort filter.
        # Priority: _FIELD_EXTRA['order'] > existing field.render_kw['order'] > default 999.
        rk['order'] = extra.get('order', rk.get('order', 999))
        field.kwargs['render_kw'] = rk

        # Add extra_validators
        if 'extra_validators' in extra:
            field.kwargs.setdefault('validators', []).extend(extra['extra_validators'])

    # Build the class dynamically so WTForms metaclass processes all fields
    return type('EventForm', (FlaskForm,), all_fields)

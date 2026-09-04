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

from flask import current_app, has_request_context, request, session
from flask_wtf import FlaskForm
from wtforms import (HiddenField, RadioField, StringField)
from wtforms.validators import ValidationError, URL

from tinker.cascade_form_helpers import (_fields_from_def,
                                          get_metadata_fields,
                                          get_structured_data_labels)

# Local
from tinker.tinker_controller import TinkerController
from tinker import app
from tinker.data_definition_parser import get_field_definitions


tinker = TinkerController()


def _flatten_event_cascade_data(data, prefix='', multiples=None, parent_instances=None):
    """Flatten nested event edit-data into WTForms field keys.

    Example:
      {'cost': {'offer': [{'price': '1'}]}}
      -> {'cost__[multiple]offer_1__price': '1'}
    """
    flat = {}
    multiples = multiples or {}
    current_parents = parent_instances or []

    if not isinstance(data, dict):
        return flat

    for key, value in data.items():
        field_key = '{}__{}'.format(prefix, key) if prefix else key

        if isinstance(value, dict):
            count_key = '__'.join(current_parents + [key]) if current_parents else key
            is_multiple_group = count_key in multiples

            if is_multiple_group:
                instance_key = '[multiple]{}_1'.format(key)
                nested_prefix = '{}__{}'.format(prefix, instance_key) if prefix else instance_key
                flat.update(_flatten_event_cascade_data(
                    value,
                    nested_prefix,
                    multiples=multiples,
                    parent_instances=current_parents + [instance_key],
                ))
            else:
                flat.update(_flatten_event_cascade_data(
                    value,
                    field_key,
                    multiples=multiples,
                    parent_instances=current_parents,
                ))
            continue

        if isinstance(value, list):
            # Multiple groups are represented as list[dict] in edit_data.
            if value and all(isinstance(item, dict) for item in value):
                for index, item in enumerate(value, start=1):
                    instance_key = '[multiple]{}_{}'.format(key, index)
                    nested_prefix = '{}__{}'.format(prefix, instance_key) if prefix else instance_key
                    flat.update(_flatten_event_cascade_data(
                        item,
                        nested_prefix,
                        multiples=multiples,
                        parent_instances=current_parents + [instance_key],
                    ))
            else:
                # SelectMultiple and metadata arrays should remain arrays.
                flat[field_key] = value
            continue

        flat[field_key] = value

    return flat


def _coerce_to_existing_field_key(key, valid_field_names):
    """Map a flattened key to an existing field name by inserting single-instance
    multiple markers when needed (for example timeDescription -> [multiple]timeDescription_1).
    """
    if key in valid_field_names:
        return key

    parts = (key or '').split('__')
    if not parts:
        return key

    candidates = ['']
    for part in parts:
        next_candidates = []
        for prefix in candidates:
            base = '{}__{}'.format(prefix, part) if prefix else part
            next_candidates.append(base)

            if part and not part.startswith('[multiple]'):
                multiple_part = '[multiple]{}_1'.format(part)
                with_multiple = '{}__{}'.format(prefix, multiple_part) if prefix else multiple_part
                next_candidates.append(with_multiple)
        candidates = next_candidates

    for candidate in candidates:
        if candidate in valid_field_names:
            return candidate

    return key


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
    'title': {
        'render_kw': {'groups': ['event_basics'], 'group_labels': ['Event basics']},
        'order': 0,
        'extra_validators': [length_checker]
    },
    'description': {
        'render_kw': {'groups': ['event_basics'], 'group_labels': ['Event basics']},
        'order': 1
    },
    # Specify metadata fields that should be hidden fields
    'hide_from_nav': {'render_kw': {'type': 'hidden'}},
    'hide_site_nav': {'render_kw': {'type': 'hidden'}},
    # Field toggles — declarative companion controls that show/hide other fields in the template.
    'hide_from_calendar': {
        'nest_within_card': True,
        'nest_card_label': 'Event metadata'
    },
    'internal': {
        'nest_within_card': True,
        'nest_card_label': 'Event metadata'
    },
    'general': {
        'nest_within_card': True,
        'nest_card_label': 'Event metadata'
    },
    'offices': {
        'toggle_with_yes_no': True,
        'toggle_default': 'No',
        'render_kw': {'show_class': 'Yes'},
        'nest_within_card': True,
        'nest_card_label': 'Event metadata'
    },
    'undergraduate_departments': {
        'toggle_with_accordion_card': True,
        'accordion_toggle_with_yes_no': True,
        'accordion_toggle_label': 'Is this event hosted by a specific department or program?',
        'accordion_toggle_default': 'No',
        'nest_within_card': True,
        'nest_card_label': 'Event metadata'
    },
    'adult_undergrad_program': {
        'toggle_with_accordion_card': True,
        'accordion_toggle_with_yes_no': True,
        'accordion_toggle_label': 'Is this event hosted by a specific department or program?',
        'accordion_toggle_default': 'No',
        'nest_within_card': True,
        'nest_card_label': 'Event metadata',
    },
    'graduate_program': {
        'toggle_with_accordion_card': True,
        'accordion_toggle_with_yes_no': True,
        'accordion_toggle_label': 'Is this event hosted by a specific department or program?',
        'accordion_toggle_default': 'No',
        'nest_within_card': True,
        'nest_card_label': 'Event metadata',
    },
    'seminary_program': {
        'toggle_with_accordion_card': True,
        'accordion_toggle_with_yes_no': True,
        'accordion_toggle_label': 'Is this event hosted by a specific department or program?',
        'accordion_toggle_default': 'No',
        'nest_within_card': True,
        'nest_card_label': 'Event metadata',
    },
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
                                                 message='Please enter a valid URL.')]}
}


def _iter_yes_no_toggle_configs():
    """Yield declarative yes/no companion-toggle config from _FIELD_EXTRA."""
    for target_name, extra in _FIELD_EXTRA.items():
        if not extra.get('toggle_with_yes_no'):
            continue
        yield {
            'target_name': target_name,
            'toggle_name': '{}_enabled'.format(target_name),
            'toggle_default': extra.get('toggle_default', 'No'),
        }


def _iter_accordion_card_toggle_configs():
    """Yield declarative grouped-accordion config from _FIELD_EXTRA."""
    for target_name, extra in _FIELD_EXTRA.items():
        if not extra.get('toggle_with_accordion_card'):
            continue
        yield {
            'target_name': target_name,
            'accordion_card_label': extra.get('accordion_card_label', 'Additional fields'),
            'nested_card_label': extra.get('nest_card_label', ''),
            'accordion_toggle_with_yes_no': bool(extra.get('accordion_toggle_with_yes_no', False)),
            'accordion_toggle_label': extra.get('accordion_toggle_label', ''),
            'accordion_toggle_default': extra.get('accordion_toggle_default', 'No'),
        }


def _iter_nested_card_configs():
    """Yield declarative nested-card config from _FIELD_EXTRA."""
    for target_name, extra in _FIELD_EXTRA.items():
        if not extra.get('nest_within_card'):
            continue
        yield {
            'target_name': target_name,
            'nested_card_label': extra.get('nest_card_label', 'Additional information'),
        }


def _yes_no_choices(default_value):
    """Return Yes/No choices with the configured default option first."""
    default_value = default_value if default_value in ('Yes', 'No') else 'No'
    other_value = 'No' if default_value == 'Yes' else 'Yes'
    return [(default_value, default_value), (other_value, other_value)]


def _normalize_yes_no_default(value):
    return value if value in ('Yes', 'No') else 'No'


# ---------------------------------------------------------------------------
# Form factory
# ---------------------------------------------------------------------------

def get_event_form(multiples={}, cascade_data=None):
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
    form_class = _build_event_form_class(multiples=multiples)

    form_kwargs = _flatten_event_cascade_data(cascade_data, multiples=multiples) if cascade_data else {}
    if form_kwargs:
        empty_form = form_class()
        valid_field_names = set(empty_form._fields.keys())
        normalized_kwargs = {}
        for key, value in form_kwargs.items():
            mapped_key = _coerce_to_existing_field_key(key, valid_field_names)
            normalized_kwargs[mapped_key] = value
        form_kwargs = normalized_kwargs

    form = form_class(**form_kwargs)

    # Keep companion yes/no toggles in sync with existing target values on initial load.
    # On submit, Flask-WTF binds posted toggle values directly from request.form.
    if not has_request_context() or not request.form:
        for toggle_cfg in _iter_yes_no_toggle_configs():
            target_name = toggle_cfg['target_name']
            toggle_name = toggle_cfg['toggle_name']
            toggle_default = toggle_cfg['toggle_default']
            target_field = form._fields.get(target_name)
            toggle_field = form._fields.get(toggle_name)
            if not target_field or not toggle_field:
                continue

            # For new forms, always honor declarative toggle_default.
            # For edit forms (cascade_data provided), infer Yes only when values exist.
            if cascade_data is None:
                toggle_field.data = toggle_default
                continue

            target_value = target_field.data
            has_value = bool(target_value)
            toggle_field.data = 'Yes' if has_value else toggle_default

        for field in form:
            rk = field.render_kw or {}
            if not rk.get('is_accordion_group_toggle'):
                continue

            controls_fields = rk.get('controls_fields') or []
            toggle_default = _normalize_yes_no_default(rk.get('accordion_toggle_default', field.default or 'No'))

            if cascade_data is None:
                field.data = toggle_default
                continue

            has_value = False
            for dep_name in controls_fields:
                dep_field = form._fields.get(dep_name)
                if dep_field and dep_field.data:
                    has_value = True
                    break
            field.data = 'Yes' if has_value else toggle_default

    for field in form:
        if getattr(field, 'type', '') != 'FileField':
            continue
        if not isinstance(field.data, str) or not field.data:
            continue

        path_field = form._fields.get(field.name + '_path')
        if path_field and not path_field.data:
            path_field.data = field.data

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

def _build_event_form_class(multiples={}):
    """
    Build and return the EventForm class with all data-definition fields
    injected alongside the fixed Cascade metadata fields.
    """

    all_fields = {}

    # Create and add the metadata fields
    metadata_fields = get_metadata_fields(tinker, app.config.get('EVENTS_METADATA_SET', ''))
    all_fields.update(metadata_fields)
    
    # Walk the full data definition tree
    # Pass event-specific field config and choice overrides to the generic helper.
    on_campus_locations = get_structured_data_labels(tinker, app.config.get('EVENTS_ON_CAMPUS_LOCATIONS', ''))
    dd_fields = _fields_from_def(
        get_field_definitions(app.config.get('EVENTS_DATA_DEF_ID', ''), multiples=multiples),
        field_extra=_FIELD_EXTRA,
        override_choices={'location': on_campus_locations},
    )
    all_fields.update(dd_fields)

    # Build declarative yes/no companion toggle controls.
    for toggle_cfg in _iter_yes_no_toggle_configs():
        target_name = toggle_cfg['target_name']
        if target_name not in all_fields:
            continue

        target_field = all_fields[target_name]
        target_rk = dict(target_field.kwargs.get('render_kw', {}) or {})
        target_groups = list(target_rk.get('groups', []))
        target_group_labels = list(target_rk.get('group_labels', []))
        target_order = target_rk.get('order', _FIELD_EXTRA.get(target_name, {}).get('order', 999))

        toggle_name = toggle_cfg['toggle_name']
        toggle_default = toggle_cfg['toggle_default']
        toggle_label = '{}?'.format(target_field.args[0] if target_field.args else target_name.replace('_', ' ').title())
        all_fields[toggle_name] = RadioField(
            toggle_label,
            choices=_yes_no_choices(toggle_default),
            default=toggle_default,
            render_kw={
                'groups': target_groups,
                'group_labels': target_group_labels,
                'order': target_order,
                'onchange': 'selectChanged(this)',
                'inline_options': True,
                'is_toggle_control': True,
                'controls_field': target_name,
            },
        )

        target_rk['toggle_field_name'] = toggle_name
        target_field.kwargs['render_kw'] = target_rk

    # Mark fields that should render in a shared accordion card.
    accordion_group_toggles = {}
    accordion_group_controls = {}
    for toggle_cfg in _iter_accordion_card_toggle_configs():
        target_name = toggle_cfg['target_name']
        if target_name not in all_fields:
            continue

        target_field = all_fields[target_name]
        target_rk = dict(target_field.kwargs.get('render_kw', {}) or {})
        group_key = '{}::{}'.format(toggle_cfg['nested_card_label'], toggle_cfg['accordion_card_label'])

        if toggle_cfg['accordion_toggle_with_yes_no']:
            accordion_group_controls.setdefault(group_key, []).append(target_name)
            if group_key not in accordion_group_toggles:
                target_groups = list(target_rk.get('groups', []))
                target_group_labels = list(target_rk.get('group_labels', []))
                target_order = target_rk.get('order', _FIELD_EXTRA.get(target_name, {}).get('order', 999))

                toggle_name = '{}_accordion_enabled'.format(target_name)
                toggle_default = _normalize_yes_no_default(toggle_cfg.get('accordion_toggle_default'))
                toggle_label = toggle_cfg.get('accordion_toggle_label') or '{}?'.format(toggle_cfg['accordion_card_label'])
                all_fields[toggle_name] = RadioField(
                    toggle_label,
                    choices=_yes_no_choices(toggle_default),
                    default=toggle_default,
                    render_kw={
                        'groups': target_groups,
                        'group_labels': target_group_labels,
                        'order': target_order - 0.01,
                        'onchange': 'selectChanged(this)',
                        'inline_options': True,
                        'is_toggle_control': True,
                        'is_accordion_group_toggle': True,
                        'accordion_toggle_default': toggle_default,
                    },
                )
                accordion_group_toggles[group_key] = toggle_name

        target_rk['external_accordion_card_label'] = toggle_cfg['accordion_card_label']
        if toggle_cfg['accordion_toggle_with_yes_no'] and group_key in accordion_group_toggles:
            target_rk['external_accordion_toggle_field_name'] = accordion_group_toggles[group_key]
            target_rk.setdefault('show_class', 'Yes')
        target_field.kwargs['render_kw'] = target_rk

    for group_key, toggle_name in accordion_group_toggles.items():
        toggle_field = all_fields.get(toggle_name)
        if not toggle_field:
            continue
        controls_fields = accordion_group_controls.get(group_key, [])
        toggle_rk = dict(toggle_field.kwargs.get('render_kw', {}) or {})
        toggle_rk['controls_fields'] = controls_fields
        toggle_field.kwargs['render_kw'] = toggle_rk

    # Mark fields that should render as full cards nested inside a shared parent card.
    for nested_cfg in _iter_nested_card_configs():
        target_name = nested_cfg['target_name']
        if target_name not in all_fields:
            continue

        target_field = all_fields[target_name]
        target_rk = dict(target_field.kwargs.get('render_kw', {}) or {})
        target_rk['nested_card_label'] = nested_cfg['nested_card_label']
        target_field.kwargs['render_kw'] = target_rk

    # Apply _FIELD_EXTRA and ensure 'order' exists for all fields to support template sorting.
    for name, field in list(all_fields.items()):
        extra = _FIELD_EXTRA.get(name, {})
        rk = dict(field.kwargs.get('render_kw', {}) or {})

        if 'render_kw' in extra:
            rk.update(extra['render_kw'])

        # Ensure 'order' is always present in render_kw for the Jinja sort filter.
        # Priority: _FIELD_EXTRA['order'] > existing field.render_kw['order'] > default 999.
        field_order = extra.get('order', rk.get('order', 999))
        rk['order'] = field_order

        # Render hidden fields as WTForms HiddenField regardless of their original type.
        if rk.get('type') == 'hidden' and field.field_class is not HiddenField:
            all_fields[name] = HiddenField(
                field.args[0] if field.args else name,
                default=field.kwargs.get('default', ''),
                render_kw=rk,
            )
            continue

        field.kwargs['render_kw'] = rk

        # Add extra_validators
        if 'extra_validators' in extra:
            field.kwargs.setdefault('validators', []).extend(extra['extra_validators'])

    # Build the class dynamically so WTForms metaclass processes all fields
    return type('EventForm', (FlaskForm,), all_fields)

# coding: utf-8
"""
Generic helpers for building WTForms-based forms from Cascade data definitions.

Any view module can import these to get:

  * CKEditorTextAreaField — marker so templates know to attach CKEditor
  * _build_field          — convert a parsed field-def dict → WTForms field
  * _fields_from_def      — walk a data-def tree → ordered {name: field} dict
  * _flatten_cascade_data — convert Cascade get_edit_data payload → form kwargs
  * _bind_nested_fieldset — recursive helper used by bind_fields

Typical usage in a view's forms module::

    from tinker.cascade_form_helpers import (
        CKEditorTextAreaField,
        _build_field, _fields_from_def,
        _flatten_cascade_data, bind_fields,
    )

    # Event-specific overrides passed in; nothing event-specific lives here.
    dd_fields = _fields_from_def(
        get_field_definitions(),
        top_level=True,
        field_extra=_FIELD_EXTRA,
        override_choices={'location': building_choices},
    )
"""

from flask import current_app
from bu_cascade.asset_tools import convert_asset
from flask_wtf.file import FileField
import re
from wtforms import (BooleanField, HiddenField, RadioField,
                     SelectField, SelectMultipleField, StringField, TextAreaField, Field)
from wtforms.validators import DataRequired, ValidationError


def _ckeditor_required(form, field):
    """
    Validator for CKEditor wysiwyg fields.

    DataRequired() passes for '<p></p>' and similar empty-paragraph HTML that
    CKEditor submits when the editor has no visible content.  This validator
    strips all HTML tags, decodes &nbsp;, and requires at least one non-
    whitespace character to be present.
    """
    stripped = re.sub(r'<[^>]+>', '', field.data or '').replace('&nbsp;', ' ').strip()
    if not stripped:
        raise ValidationError('This field is required.')


# WTForms reads this attribute to set field.flags.required, which templates
# use to display the "required" label.
_ckeditor_required.field_flags = ('required',)


# ---------------------------------------------------------------------------
# Cascade metadataset helpers
# ---------------------------------------------------------------------------

def get_metadata_fields(tinker_controller, metadata_path):
    """
    Read the Cascade metadataset at *metadata_path* and return:

      built_in_fields -- dict of WTForms UnboundFields, one StringField per
                         built-in metadata field whose visibility is 'inline'
                         (e.g. title, teaser).
      metadata_set    -- raw metadataSet dict, to be passed to
                         build_metadata_custom_fields() *after* any other
                         WTForms fields whose creation_counter should be lower
                         (i.e. fields that should appear earlier in the form).
    """
    raw = tinker_controller.read(metadata_path, 'metadataset')
    #current_app.logger.debug(f"Metadata for {metadata_path}: {json.dumps(raw, default=str)}")
    metadata_set = convert_asset(raw['asset']['metadataSet'])  # normalize here

    # Create the Built-in inline fields
    built_in_fields = {}
    for key, value in metadata_set.items():
        if not key.endswith('FieldVisibility') or value != 'inline':
            continue
        name = key[:-len('FieldVisibility')]
        label = name.capitalize()
        required = metadata_set.get(name + 'FieldRequired', False)
        help_text = metadata_set.get(name + 'FieldHelpText', '')
        validators = [DataRequired()] if required else []
        built_in_fields[name] = StringField(label, validators=validators, description=help_text)

    # Create the custom metadata fields
    custom_fields = build_metadata_custom_fields(metadata_set)

    return {**built_in_fields, **custom_fields}


def build_metadata_custom_fields(metadata_set):
    """
    Build and return a dict of WTForms UnboundFields for the dynamic metadata
    field definitions in *metadata_set* (multiselect → SelectMultipleField,
    radio → RadioField).

    Call this *after* instantiating any form fields that should appear before
    these in the rendered form, since WTForms orders fields by creation_counter.
    """
    raw_defs = metadata_set['dynamicMetadataFieldDefinitions']['dynamicMetadataFieldDefinition']
    if isinstance(raw_defs, dict):
        raw_defs = [raw_defs]

    custom_fields = {}
    for item in raw_defs:
        if item.get('visibility', '').lower() == 'hidden':
            continue
        name = item['name'].replace('-', '_')
        label = item.get('label', name)
        required = item.get('required', False)
        help_text = item.get('helpText', '')
        field_type = item.get('fieldType', 'text')
        validators = [DataRequired()] if required else []
        raw_vals = item.get('possibleValues', {}).get('possibleValue', [])
        if isinstance(raw_vals, dict):
            raw_vals = [raw_vals]
        choices = [(v['value'], v['value']) for v in raw_vals if isinstance(v, dict)]

        # Find all values with selectedByDefault true
        default_values = [v['value'] for v in raw_vals if isinstance(v, dict) and v.get('selectedByDefault') in (True, 'true', 'True')]
        if field_type == 'multiselect':
            custom_fields[name] = SelectMultipleField(
                label, choices=choices, default=default_values or ['None'],
                description=help_text, validators=validators)
        elif field_type == 'radio':
            default_radio = default_values[0] if default_values else None
            custom_fields[name] = RadioField(
                label, choices=choices, default=default_radio,
                description=help_text, validators=validators)

    return custom_fields


def get_structured_data_labels(tinker_controller, block_id):
    """
    Read an xhtmlDataDefinitionBlock from Cascade and return its label values
    as WTForms SelectField choices: [('', '-select-'), (label, label), ...]
    sorted alphabetically.

    Expects each top-level structuredDataNode to be a group whose children
    include a node with identifier 'label' containing the display text.
    """
    raw = tinker_controller.read(block_id, type='block')
    nodes = (raw['asset']['xhtmlDataDefinitionBlock']['structuredData']
             ['structuredDataNodes']['structuredDataNode'])
    labels = []
    for group in nodes:
        children = group.get('structuredDataNodes', {}).get('structuredDataNode', [])
        for child in children:
            if child.get('identifier') == 'label':
                label = (child.get('text') or '').strip()
                if label:
                    labels.append((label, label))
                break
    labels.sort(key=lambda x: x[0])
    return [('', '-select-')] + labels


# ---------------------------------------------------------------------------
# Marker class — template uses isinstance check to attach CKEditor
# ---------------------------------------------------------------------------

class CKEditorTextAreaField(TextAreaField):
    pass


def _is_truthy_default(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in ('yes', 'true', '1', 'on')


# ---------------------------------------------------------------------------
# Data-definition → WTForms field converter
# ---------------------------------------------------------------------------

def _build_field(field_def, field_extra=None, override_choices=None):
    """
    Convert a parsed field-def dict into a WTForms UnboundField.

    field_extra      -- dict keyed by bare identifier with optional sub-keys:
                        'extra_validators' (list) and 'render_kw' (dict).
                        Mirrors the _FIELD_EXTRA pattern used in individual
                        view modules for field-specific customisation.
    override_choices -- dict mapping bare identifier → [(value, label), ...]
                        for dropdowns whose choices should come from application
                        logic rather than the data definition (e.g. buildings).

    Returns None if field_def is empty/falsy.
    """
    if not field_def:
        return None

    fe = field_extra or {}
    oc = override_choices or {}

    identifier = field_def.get('identifier', '')
    extra      = fe.get(identifier, {})
    ftype      = field_def.get('type', 'text')
    label      = field_def['label']
    help_text  = field_def.get('help_text', '')
    required   = field_def.get('required', False)
    # Use default from data definition if present, else from field_extra
    default = field_def.get('default') if field_def.get('default') is not None else extra.get('default', '')

    validators = [DataRequired()] if required else []
    validators.extend(extra.get('extra_validators', []))
    kw = dict(extra.get('render_kw', {}))

    if kw.get('type') == 'hidden':
        return HiddenField(label, default=default, render_kw=kw)

    if ftype == 'datetime':
        # Use StringField — the datepicker submits "Month Dth YYYY, HH:MM AM/PM"
        # which change_dates() parses server-side.  WTForms' DateTimeField would
        # reject that format with "Not a valid datetime value".
        # Set class="datepicker" so the JS widget initialises on the input even
        # though the template no longer sees type "DateTimeField".
        kw.setdefault('class', 'datepicker')
        return StringField(label, description=help_text,
                           validators=validators or [], render_kw=kw)

    if ftype == 'checkbox':
        choices = field_def.get('choices', [])
        if len(choices) > 1:
            choice_pairs = [(c['value'], c['label'] or c['value']) for c in choices]
            selected_defaults = [c['value'] for c in choices if c.get('selected')]
            if not selected_defaults and field_def.get('default'):
                selected_defaults = [field_def.get('default')]
            kw['_widget'] = 'checkbox-group'
            return SelectMultipleField(label, choices=choice_pairs, default=selected_defaults,
                                       description=help_text, validators=validators, render_kw=kw)
        if choices and 'value' not in kw:
            kw['value'] = choices[0].get('value', '')
        selected_default = any(c.get('selected') for c in choices)
        bool_default = selected_default or _is_truthy_default(field_def.get('default'))
        return BooleanField(label, description=help_text,
                            validators=validators, render_kw=kw, default=bool_default)

    if ftype == 'multi-selector':
        choices = [(c['value'], c['label'] or c['value']) for c in field_def.get('choices', [])]
        return SelectMultipleField(label, choices=choices, default=[],
                                   description=help_text, validators=validators, render_kw=kw)

    if ftype == 'dropdown':
        choices = oc.get(identifier) or [(c['value'], c['label']) for c in field_def.get('choices', [])]
        return SelectField(label, choices=choices, default=default,
                           validators=validators, render_kw=kw)

    if ftype == 'radiobutton':
        choices = [(c['value'], c['label'] or c['value']) for c in field_def.get('choices', [])]
        return RadioField(label, choices=choices, default=default,
                          description=help_text, validators=validators, render_kw=kw)

    if ftype == 'wysiwyg':
        # Replace DataRequired with _ckeditor_required: CKEditor submits non-empty
        # HTML (e.g. '<p></p>') for a visually empty editor, which DataRequired
        # treats as valid.  _ckeditor_required strips tags before checking.
        wysiwyg_validators = [
            _ckeditor_required if isinstance(v, DataRequired) else v
            for v in validators
        ]
        return CKEditorTextAreaField(label, description=help_text,
                                     validators=wysiwyg_validators, render_kw=kw)

    if ftype == 'multiline':
        return TextAreaField(label, description=help_text,
                             validators=validators, render_kw=kw)

    if ftype == 'file':
        return FileField(label, description=help_text, render_kw=kw)

    # 'text' or anything else → StringField
    return StringField(label, description=help_text,
                       validators=validators, render_kw=kw, default=default)


# ---------------------------------------------------------------------------
# Recursive data-definition tree walker → returns flat {name: field} dict
# ---------------------------------------------------------------------------

def _fields_from_def(field_defs, prefix='', top_level=False,
                     field_extra=None, override_choices=None):
    """
    Walk a list of field-def dicts and return an ordered dict of
    {form_field_name: UnboundField}.

    At nested levels, non-repeating groups continue to be expanded inline.

    field_extra      -- see _build_field
    override_choices -- see _build_field
    """

    fe = field_extra or {}
    oc = override_choices or {}
    result = {}

    def add_group_ancestry(field, parent_groups, parent_labels):
        if hasattr(field, 'kwargs'):
            rk = dict(field.kwargs.get('render_kw', {}))
            # Immediate parent group/label (last in ancestry, if any)
            rk['group'] = parent_groups[-1] if parent_groups else None
            rk['group_label'] = parent_labels[-1] if parent_labels else None
            rk['groups'] = parent_groups or []
            rk['group_labels'] = parent_labels or []
            field.kwargs['render_kw'] = rk

    def _fields_from_def_inner(field_defs, prefix='', parent_groups=None, parent_labels=None):
        res = {}
        for fd in field_defs:
            identifier = fd.get('identifier', '')
            name = (prefix + '__' + identifier) if prefix else identifier

            if fd['type'] == 'group':
                children = fd.get('children', [])
                group_label = fd.get('label', identifier)
                # Recursively pass down ancestry, including this group
                new_parent_groups = (parent_groups or []) + [identifier]
                new_parent_labels = (parent_labels or []) + [group_label]
                child_fields = _fields_from_def_inner(
                    children,
                    prefix=name,
                    parent_groups=new_parent_groups,
                    parent_labels=new_parent_labels,
                )
                for child_name, field in child_fields.items():
                    res[child_name] = field
            else:
                field = _build_field(fd, field_extra=fe, override_choices=oc)
                if field is not None:
                    # Set ancestry for leaf fields only
                    add_group_ancestry(field, parent_groups, parent_labels)
                    res[name] = field
                    if fd.get('type') == 'file':
                        existing_rk = dict(field.kwargs.get('render_kw', {}))
                        path_rk = {k: v for k, v in existing_rk.items() if k != 'show_class'}
                        res[name + '_path'] = HiddenField(
                            fd['label'] + ' (path)', render_kw=path_rk)
        return res

    result = _fields_from_def_inner(field_defs, prefix=prefix, parent_groups=[], parent_labels=[])


    # Always apply show_fields logic so all dropdowns with show-fields get onchange, even nested
    _apply_show_fields(result, field_defs)

    return result


def _set_field_show_class(field, show_class):
    """Set show_class on an UnboundField without overwriting an existing value."""
    rk = dict(field.kwargs.get('render_kw', {}))
    if 'show_class' not in rk:
        rk['show_class'] = show_class
        field.kwargs['render_kw'] = rk


def _apply_show_fields(result, field_defs, prefix=''):
    """
    Walk field_defs and for every dropdown that has show_fields on any choice:
      1. Add onchange='selectChanged(this)' to the dropdown field's render_kw.
      2. Set show_class=<option_value> on every field whose name starts with
         the resolved target path.

    Paths in show_fields are absolute from the data-definition root
    (e.g. 'featuredVisual/image'), converted to form names by replacing
    '/' with '__'.  If the resolved name is not directly in result (i.e. the
    target was a group that was inline-expanded), all fields whose name starts
    with '<target>__' receive the show_class.
    """
    for fd in field_defs:
        identifier = fd.get('identifier', '')
        name = (prefix + '__' + identifier) if prefix else identifier

        if fd['type'] == 'group':
            _apply_show_fields(result, fd.get('children', []), prefix=name)
        elif fd['type'] == 'dropdown':
            show_choices = [c for c in fd.get('choices', []) if c.get('show_fields')]
            if not show_choices:
                continue

            # Add onchange to the dropdown itself
            suffix = '__' + identifier
            for field_name, field in result.items():
                if field_name.endswith(suffix) and hasattr(field, 'kwargs'):
                    rk = dict(field.kwargs.get('render_kw', {}))
                    if 'onchange' not in rk:
                        rk['onchange'] = 'selectChanged(this)'
                        field.kwargs['render_kw'] = rk

            # Apply show_class to each target field (or group of fields)
            for choice in show_choices:
                target_name = choice['show_fields'].replace('/', '__')
                option_value = choice['value']
                if target_name in result:
                    _set_field_show_class(result[target_name], option_value)
                else:
                    # Group was inline-expanded — apply show_class to all children
                    child_prefix = target_name + '__'
                    for field_name, field in result.items():
                        if field_name.startswith(child_prefix):
                            _set_field_show_class(field, option_value)

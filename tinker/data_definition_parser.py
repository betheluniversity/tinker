# coding: utf-8
"""
Generic Cascade data-definition fetcher and parser.

Any view module can use this to read and parse a Cascade data definition by
its asset ID.  The parsed field-def tree is cached per ID so repeated calls
within the cache window (1 hour) do not hit the Cascade API.

Typical usage::

    from tinker.data_definition_parser import get_field_definitions, get_group_def

    field_defs = get_field_definitions(app.config['MY_DATA_DEF_ID'])
    date_group = get_group_def(app.config['MY_DATA_DEF_ID'], 'date')
"""
import json
from xml.etree import ElementTree as ET

from tinker import app, cache
from tinker.tinker_controller import TinkerController

_tinker = TinkerController()


# ---------------------------------------------------------------------------
# XML fetch + cache
# ---------------------------------------------------------------------------

def _fetch_data_def_xml(data_def_id):
    """
    Fetch the data definition XML from Cascade and return the root Element.
    Returns None if the ID is empty or the asset has no XML body.
    """
    if not data_def_id:
        return None

    dd = _tinker.read_datadefinition(data_def_id)
    asset, _, _ = dd.get_asset()
    xml_str = asset.get('dataDefinition', {}).get('xml', '')
    if not xml_str:
        return None

    return ET.fromstring(xml_str)


@cache.memoize(timeout=3600)
def _fetch_data_def_xml_memoized(data_def_id):
    return _fetch_data_def_xml(data_def_id)


def _fetch_data_def_xml_cached(data_def_id):
    if app.config.get('ENVIRON') == 'prod':
        return _fetch_data_def_xml_memoized(data_def_id)
    return _fetch_data_def_xml(data_def_id)


# ---------------------------------------------------------------------------
# Low-level XML helpers
# ---------------------------------------------------------------------------

def _find_group(root, *path):
    """
    Walk a sequence of group identifiers from *root* and return the matching
    Element, or None if any step is missing.
    """
    current = root
    for identifier in path:
        match = None
        for child in current:
            if child.get('identifier') == identifier:
                match = child
                break
        if match is None:
            return None
        current = match
    return current


def _dropdown_choices(element, include_blank=False):
    """
    Return a list of ``(value, label)`` tuples from ``<dropdown-item>``
    children of *element*.
    """
    choices = []
    if include_blank:
        choices.append(('', '-select-'))
    for item in element.findall('dropdown-item'):
        value = item.get('value', '')
        label = item.get('label', value)
        choices.append((value, label))
    return choices


# ---------------------------------------------------------------------------
# Element parser
# ---------------------------------------------------------------------------

def _parse_element(element):
    """
    Recursively parse an XML element into a plain dict.

    Returned keys:
      All types:  identifier, label, type, required, default
      group    :  multiple (bool), children (list of dicts)
      dropdown :  choices (list of {value, label, show_fields}), allow_custom
      checkbox :  choices (list of {value, label})
      text / wysiwyg / datetime / file:  help_text
    """
    tag = element.tag
    identifier = element.get('identifier', '')
    label = element.get('label', '')
    required = element.get('required', 'false') == 'true'
    default = element.get('default', '')

    if tag == 'group':
        return {
            'identifier': identifier,
            'label': label,
            'type': 'group',
            'required': required,
            'multiple': element.get('multiple', 'false') == 'true',
            'children': [
                _parse_element(child)
                for child in element
                if child.tag in ('text', 'asset', 'group')
            ],
        }

    help_text = element.get('help-text', '')
    field_type = element.get('type', '')
    wysiwyg = element.get('wysiwyg', 'false') == 'true'

    if tag == 'asset':
        return {
            'identifier': identifier,
            'label': label,
            'type': 'file',
            'required': required,
            'default': default,
            'help_text': help_text,
        }

    # tag == 'text'
    if field_type == 'datetime':
        return {
            'identifier': identifier,
            'label': label,
            'type': 'datetime',
            'required': required,
            'default': default,
            'help_text': help_text,
        }
    if field_type == 'checkbox':
        checkbox_choices = [
            {
                'value': ci.get('value', ''),
                'label': ci.get('label', ''),
                'selected': (
                    str(ci.get('checked', 'false')).strip().lower() == 'true'
                ),
            }
            for ci in element.findall('checkbox-item')
        ]

        # Some data definitions mark the default checked item via checkbox-item
        # selected/selectedByDefault attributes instead of the parent default attr.
        if not default:
            selected_values = [c.get('value', '') for c in checkbox_choices if c.get('selected')]
            default = selected_values[0] if selected_values else default

        return {
            'identifier': identifier,
            'label': label,
            'type': 'checkbox',
            'required': required,
            'default': default,
            'help_text': help_text,
            'choices': checkbox_choices,
        }
    if field_type == 'dropdown':
        return {
            'identifier': identifier,
            'label': label,
            'type': 'dropdown',
            'required': required,
            'default': default,
            'help_text': help_text,
            'allow_custom': element.get('allow-custom-values', 'false') == 'true',
            'choices': [
                {
                    'value': di.get('value', ''),
                    'label': di.get('label', ''),
                    'show_fields': di.get('show-fields', '').replace('metadata-field-placeholder-', ''),
                }
                for di in element.findall('dropdown-item')
            ],
        }
    if field_type == 'radiobutton':
        return {
            'identifier': identifier,
            'label': label,
            'type': 'radiobutton',
            'required': required,
            'default': default,
            'help_text': help_text,
            'choices': [
                {
                    'value': ri.get('value', ''),
                    'label': ri.get('label', ri.get('value', '')),
                    'show_fields': ri.get('show-fields', '').replace('metadata-field-placeholder-', ''),
                }
                for ri in element.findall('radio-item')
            ],
        }
    if field_type == 'multi-selector':
        return {
            'identifier': identifier,
            'label': label,
            'type': 'multi-selector',
            'required': required,
            'default': default,
            'help_text': help_text,
            'choices': [
                {'value': si.get('value', ''), 'label': si.get('label', si.get('value', ''))}
                for si in element.findall('selector-item')
            ],
        }
    if wysiwyg:
        return {
            'identifier': identifier,
            'label': label,
            'type': 'wysiwyg',
            'required': required,
            'default': default,
            'help_text': help_text,
        }
    if element.get('multi-line') == 'true':
        return {
            'identifier': identifier,
            'label': label,
            'type': 'multiline',
            'required': required,
            'default': default,
            'help_text': help_text,
        }
    return {
        'identifier': identifier,
        'label': label,
        'type': 'text',
        'required': required,
        'default': default,
        'help_text': help_text,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_field_definitions(data_def_id, multiples={}):
    """
    Return the full parsed data definition as a list of field-def dicts for
    the given *data_def_id*.  Returns an empty list if the definition is
    unavailable.
    """
    try:
        root = _fetch_data_def_xml_cached(data_def_id)
        if root is None:
            return []
        fields = [
            _parse_element(child)
            for child in root
            if child.tag in ('text', 'asset', 'group')
        ]
        # Output fields as json
        # app.logger.debug('get_field_definitions: parsed fields for id=%s: %s', data_def_id, json.dumps(fields))
        
        multiples = multiples or {}

        def get_multiple_count(parent_multiple_instances, group_identifier):
            count_key = '__'.join(parent_multiple_instances + [group_identifier]) if parent_multiple_instances else group_identifier
            raw_count = multiples.get(count_key, multiples.get(group_identifier, 1))
            try:
                count = int(raw_count)
            except (TypeError, ValueError):
                count = 1
            return max(count, 1)

        def expand_group_defs(defs, parent_multiple_instances=None):
            expanded = []
            current_parents = parent_multiple_instances or []

            for field_def in defs:
                if field_def.get('type') != 'group':
                    expanded.append(field_def)
                    continue

                children = field_def.get('children', [])

                if field_def.get('multiple'):
                    group_identifier = field_def.get('identifier', '')
                    instance_count = get_multiple_count(current_parents, group_identifier)
                    base_label = field_def.get('label', '') or ''

                    for i in range(1, instance_count + 1):
                        instance_identifier = f"[multiple]{group_identifier}_{i}"
                        duplicated_group = {
                            **field_def,
                            'identifier': instance_identifier,
                            'label': f"{base_label} {i}" if base_label else '',
                            'multiple': False,
                            'children': expand_group_defs(children, current_parents + [instance_identifier]),
                        }
                        expanded.append(duplicated_group)
                else:
                    expanded.append({
                        **field_def,
                        'children': expand_group_defs(children, current_parents),
                    })

            return expanded

        return expand_group_defs(fields, parent_multiple_instances=[])
    except Exception:
        app.logger.exception(
            'data_definition_parser: failed to parse field definitions for id=%s',
            data_def_id,
        )
        return []


def get_group_def(data_def_id, *path):
    """
    Walk an identifier path through the field definitions and return the
    matching dict, or None if any step is not found.

    Examples::

        get_group_def(MY_ID, 'date')
        get_group_def(MY_ID, 'location', 'offCampusLocation')
    """
    try:
        current_list = get_field_definitions(data_def_id)
        found = None
        for path_id in path:
            found = next(
                (d for d in current_list if d.get('identifier') == path_id),
                None,
            )
            if found is None:
                return None
            current_list = found.get('children', [])
        return found
    except Exception:
        app.logger.exception(
            'data_definition_parser: get_group_def failed for id=%s path=%s',
            data_def_id, path,
        )
        return None

__author__ = 'ces55739'

# tinker
from metadata import data_to_add
from tinker.web_services import *
from xml.sax.saxutils import escape
import xml.etree.ElementTree as Et

from flask import Blueprint, render_template, abort, request

sync_blueprint = Blueprint('sync_blueprint', __name__, template_folder='templates')

@sync_blueprint.route('/')
def home():
    return render_template('sync-home.html', **locals())


@sync_blueprint.route('/all')
def show():
    # don't pull locally. It's just a bad idea.
    if 'User' not in app.config['INSTALL_LOCATION']:
        import commands
        commands.getoutput("cd " + app.config['INSTALL_LOCATION'] + "; git fetch --all; git reset --hard origin/master")

    sync_metadataset(app.config['METADATA_EVENT_ID'])
    sync_metadataset(app.config['METADATA_ROBUST_ID'])
    sync_metadataset(app.config['METADATA_JOB_POSTING_ID'])
    sync_faculty_bio_data_definition(app.config['DATA_DEF_FACULTY_BIO_ID'])

    ## pass on the current values.
    school = data_to_add['school']
    undergrad_programs = data_to_add['department']
    adult_undergrad_programs = data_to_add['adult-undergrad-program']
    graduate_programs = data_to_add['graduate-program']
    seminary_programs = data_to_add['seminary-program']

    return render_template('sync.html', **locals())


def sync_faculty_bio_data_definition(data_definition_id):
    if not data_definition_id or not read(data_definition_id, 'datadefinition'):
        return None

    asset = read(data_definition_id, 'datadefinition').asset.dataDefinition
    dd = asset.xml

    structure = Et.fromstring(dd)

    # check top level element
    for el in structure:
        if "job-titles" in el.attrib['identifier']:
            # find everything in the group of job-titles that needs to be replaced.
            for next_el in el:
                if next_el.attrib['identifier'] in data_to_add:

                    # remove old elements
                    store_elements_to_remove = []
                    for el_to_remove in next_el:
                        store_elements_to_remove.append(el_to_remove)
                    for el_to_remove in store_elements_to_remove:
                        next_el.remove(el_to_remove)

                    # add new elements
                    for value in data_to_add[next_el.attrib['identifier']]:
                        if next_el.attrib['identifier'] == 'school':
                            if value == "Bethel University":
                                show_field_value = "job-titles/job_title"
                            elif value == "College of Arts and Sciences":
                                show_field_value = "job-titles/department"
                            elif value == "College of Adult & Professional Studies":
                                show_field_value = "job-titles/adult-undergrad-program"
                            elif value == "Graduate School":
                                show_field_value = "job-titles/graduate-program"
                            elif value == "Bethel Seminary":
                                show_field_value = "job-titles/seminary-program"
                            next_el.append(Et.Element('dropdown-item', {"value": value.replace('&', 'and'), "show-fields": show_field_value}))
                            # next_el.append(Et.Element('dropdown-item', {"value": value.replace('&', 'and')}))
                        else:
                            next_el.append(Et.Element('dropdown-item', {"value": value}))

    new_asset = {
        'dataDefinition': {
            'xml': Et.tostring(structure).replace('&', '&amp;'),

            'id': asset.id,
            'name': asset.name,
            'parentContainerId': asset.parentContainerId,
            'parentContainerPath': asset.parentContainerPath,
            'path': asset.path,
            'siteId': asset.siteId,
            'siteName': asset.siteName,
        }
    }

    resp = edit(new_asset)
    app.logger.warn(time.strftime("%c") + ": Faculty bio data definition synced, id: " + data_definition_id)
    return resp


def sync_metadataset(metadataset_id):
    if not metadataset_id or not read(metadataset_id, 'metadataset'):
        return None

    asset = read(metadataset_id, 'metadataset').asset.metadataSet

    metadata_elements = []
    for el in asset.dynamicMetadataFieldDefinitions.dynamicMetadataFieldDefinition:
        # create new element
        new_element = {
            'name': el.name,
            'fieldType': el.fieldType,
            'label': el.label,
            'required': el.required,
            'visibility': el.visibility
        }

        # add value/values to element
        if el.fieldType != 'text':
            # if its in the metadata.py check

            # else, just pass it over
            values_to_add = []

            if el.name in data_to_add:
                # add values from metadata.py
                for value in data_to_add[el.name]:
                    if value == 'None' or value == 'Select':
                        selected_by_default = '1'
                    else:
                        selected_by_default = '0'
                    values_to_add.append({
                            'selectedByDefault': selected_by_default,
                            'value': value.encode('utf-8')
                        })
            else:
                for value in el.possibleValues.possibleValue:
                    values_to_add.append({
                            'selectedByDefault': value.selectedByDefault,
                            'value': value.value.encode('utf-8')
                        })

            new_element['possibleValues'] = {'possibleValue': values_to_add}
        else:
            new_element['possibleValues'] = el.possibleValues.encode('utf-8')

        # add element to list
        metadata_elements.append(new_element)

    # Set the new metadata set
    dynamicMetadataFieldDefinitions = {
        'dynamicMetadataFieldDefinition': metadata_elements
    }

    # I couldn't find a good way to automatically create these. All are pulled fully from the asset besides
    # dynamicMetadataFieldDefinitions.
    new_asset = {
        'metadataSet': {
            'dynamicMetadataFieldDefinitions': dynamicMetadataFieldDefinitions,

            'authorFieldRequired': asset.authorFieldRequired,
            'authorFieldVisibility': asset.authorFieldVisibility,
            'descriptionFieldRequired': asset.descriptionFieldRequired,
            'descriptionFieldVisibility': asset.descriptionFieldVisibility,
            'displayNameFieldRequired': asset.displayNameFieldRequired,
            'displayNameFieldVisibility': asset.displayNameFieldVisibility,
            'endDateFieldRequired': asset.endDateFieldRequired,
            'endDateFieldVisibility': asset.endDateFieldVisibility,
            'id': asset.id,
            'keywordsFieldRequired': asset.keywordsFieldRequired,
            'keywordsFieldVisibility': asset.keywordsFieldVisibility,
            'name': asset.name,
            'parentContainerId': asset.parentContainerId,
            'parentContainerPath': asset.parentContainerPath,
            'path': asset.path,
            'reviewDateFieldRequired': asset.reviewDateFieldRequired,
            'reviewDateFieldVisibility': asset.reviewDateFieldVisibility,
            'siteId': asset.siteId,
            'siteName': asset.siteName,
            'startDateFieldRequired': asset.startDateFieldRequired,
            'startDateFieldVisibility': asset.startDateFieldVisibility,
            'summaryFieldRequired': asset.summaryFieldRequired,
            'summaryFieldVisibility': asset.summaryFieldVisibility,
            'teaserFieldRequired': asset.teaserFieldRequired,
            'teaserFieldVisibility': asset.teaserFieldVisibility,
            'titleFieldRequired': asset.titleFieldRequired,
            'titleFieldVisibility': asset.titleFieldVisibility,
        }
    }

    resp = edit(new_asset)
    app.logger.warn(time.strftime("%c") + ": Faculty bio metadata set synced, id: " + metadataset_id)
    return resp


def recursive_structure_build(xml):
    to_return = []
    if len(list(xml)) > 0:
        for elem in xml:
            if 'type' in elem.attrib and (elem.attrib['type'] == "dropdown"
                                          or elem.attrib['type'] == "radiobutton"):
                list_of_options = (elem.tag, elem.attrib, 0) + ([el.attrib['value'] for el in list(elem)],)
                to_return.append(list_of_options)
            else:
                children_to_append = recursive_structure_build(elem)
                if len(children_to_append) > 0:
                    to_return.append((elem.tag, elem.attrib, len(children_to_append)))
                    to_return.append(children_to_append)
                else:
                    to_return.append((elem.tag, elem.attrib, 0))
    return to_return

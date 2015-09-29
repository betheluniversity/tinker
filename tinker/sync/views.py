__author__ = 'ces55739'

# tinker
from metadata import *
from tinker.web_services import *

from flask import Blueprint, render_template, abort, request

sync_blueprint = Blueprint('sync_blueprint', __name__, template_folder='templates')

@sync_blueprint.route('/')
def show():
    asset =  read('055ce7928c5865135795f1af5935723a', 'metadataset').asset.metadataSet

    elements = []
    for el in asset.dynamicMetadataFieldDefinitions.dynamicMetadataFieldDefinition:
        new_element = {
            'name': el.name,
            'fieldType': el.fieldType,
            'label': el.label,
            'required': el.required,
            'visibility': el.visibility
        }

        if el.fieldType != 'text':
            # if its in the metadata.py check

            # else, just pass it over
            values_to_add = []
            for value in el.possibleValues.possibleValue:
                values_to_add.append({
                    'possibleValue': {
                        'selectedByDefault': value.selectedByDefault,
                        'value': value.value.encode('utf-8')
                    }
                })
            new_element['possibleValues'] = values_to_add
        else:
            new_element['possibleValues'] = el.possibleValues.encode('utf-8')

        elements.append(new_element)


        # if el.name == 'adult-undergrad-program':
        #     for val in el.possibleValues.possibleValue:
        #         print val.value


    ## Todo: get id/siteId/etc.
    ## Todo: test it
    ## Todo: hook up metadata.py
    # Set the new metadata set
    dynamicMetadataFieldDefinitions = {
        'dynamicMetadataFieldDefinition': elements
    }

    asset = {
        'metadataSet': {
            'id': asset.id,
            'name': asset.name,
            'siteId': asset.siteId,
            'parentContainerPath': asset.parentContainerPath,
            'dynamicMetadataFieldDefinitions': dynamicMetadataFieldDefinitions,
        }
    }

    resp = edit(asset)
    # print resp

    return render_template('sync.html', **locals())
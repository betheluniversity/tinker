__author__ = 'ces55739'
from roles.roledata import uid, portal
from sync.metadata import data_to_add

# python
from BeautifulSoup import *
import urllib
from datetime import datetime

# flask
from flask import Blueprint, render_template, abort, request

# tinker
from tinker.web_services import *
from xml.sax.saxutils import escape
import xml.etree.ElementTree as Et

admin_blueprint = Blueprint('admin_blueprint', __name__, template_folder='templates')
blink_roles = '/blink-roles'
sync = '/sync'
publish_manager = '/publish-manager'

@admin_blueprint.before_request
def before_request():
    if 'Administrators' not in session['groups']:
        abort(403)

@admin_blueprint.route('/blink-roles')
def blink_roles_home():
    uid_list = uid
    portal_list = portal
    return render_template('blink-roles-home.html', **locals())


@admin_blueprint.route(sync)
def sync_home():
    return render_template('sync-home.html', **locals())


@admin_blueprint.route(sync + '/all')
def show():
    # don't pull locally. It's just a bad idea.
    if 'User' not in app.config['INSTALL_LOCATION']:
        import commands
        commands.getoutput("cd " + app.config['INSTALL_LOCATION'] + "; git fetch --all; git reset --hard origin/master")

    sync_metadataset(app.config['METADATA_EVENT_ID'])
    sync_metadataset(app.config['METADATA_ROBUST_ID'])
    sync_metadataset(app.config['METADATA_JOB_POSTING_ID'])
    sync_faculty_bio_data_definition(app.config['DATA_DEF_FACULTY_BIO_ID'])
    sync_faculty_bio_data_definition(app.config['DATA_DEF_PROGRAM_FEED_ID'])
    sync_faculty_bio_data_definition(app.config['DATA_DEF_PROGRAM_BLOCK_ID'])

    # pass on the current values.
    school = data_to_add['school']
    undergrad_programs = data_to_add['department']
    adult_undergrad_programs = data_to_add['adult-undergrad-program']
    graduate_programs = data_to_add['graduate-program']
    seminary_programs = data_to_add['seminary-program']
    locations = data_to_add['location']

    # another dummy comment
    return render_template('sync.html', **locals())


def sync_faculty_bio_data_definition(data_definition_id):
    if not data_definition_id or not read(data_definition_id, 'datadefinition'):
        return None

    asset = read(data_definition_id, 'datadefinition').asset.dataDefinition
    dd = asset.xml

    structure = Et.fromstring(dd)

    # check top level element
    for el in structure:
        if not el:
            continue
        if "job-titles" in el.attrib['identifier']:  # for Faculty Bios | school, undergrad, adult-undergrad, graduate, seminary
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
                            elif value == "College of Arts & Sciences":
                                show_field_value = "job-titles/department, job-titles/department-chair, job-titles/job_title"
                            elif value == "College of Adult & Professional Studies":
                                show_field_value = "job-titles/adult-undergrad-program, job-titles/program-director, job-titles/job_title"
                            elif value == "Graduate School":
                                show_field_value = "job-titles/graduate-program, job-titles/program-director, job-titles/job_title"
                            elif value == "Bethel Seminary":
                                show_field_value = "job-titles/seminary-program, job-titles/lead-faculty, job-titles/job_title"
                            next_el.append(Et.Element('dropdown-item', {"value": value.replace('&', 'and'), "show-fields": show_field_value}))
                        else:
                            next_el.append(Et.Element('dropdown-item', {"value": value}))

        elif "program_filters" in el.attrib['identifier']:  # for Program Feeds | location
            for next_el in el:
                if next_el.attrib['identifier'] == 'location':
                    # remove old elements
                    store_elements_to_remove = []
                    for el_to_remove in next_el:
                        store_elements_to_remove.append(el_to_remove)
                    for el_to_remove in store_elements_to_remove:
                        next_el.remove(el_to_remove)

                    # add new elements
                    for value in data_to_add[next_el.attrib['identifier']]:
                        next_el.append(Et.Element('checkbox-item', {"value": value}))

        elif "concentration" in el.attrib['identifier']:  # for Program Blocks | location
            for second_el in el:
                if second_el.attrib['identifier'] == 'concentration_banner':
                    for third_el in second_el:
                        if third_el.attrib['identifier'] == 'cohort_details':
                            for fourth_el in third_el:
                                if fourth_el.attrib['identifier'] == 'location':
                                    # remove old elements
                                    store_elements_to_remove = []
                                    for el_to_remove in fourth_el:
                                        store_elements_to_remove.append(el_to_remove)
                                    for el_to_remove in store_elements_to_remove:
                                        fourth_el.remove(el_to_remove)

                                    # add new elements
                                    for value in data_to_add['location']:
                                        fourth_el.append(Et.Element('dropdown-item', {"value": value}))

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
        if not el:
            continue

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

@admin_blueprint.route(publish_manager)
def publish_home():
    #get_user()
    #not sure if this is needed -n-li
    username = session['username']

    if username == 'celanna' or username == 'ces55739' or username == 'nal64753':
        return render_template('publish-home.html', **locals())
    else:
        abort(403)

@admin_blueprint.route(publish_manager + "/program-feeds", methods=['get', 'post'])
def publish_program_feeds():
    return render_template('publish-program-feeds.html', **locals())

@admin_blueprint.route(publish_manager + "/program-feeds/<destination>", methods=['get', 'post'])
def publish_program_feeds_return(destination=''):
    if destination != "production":
        destination = "staging"

    # get results
    results = search_data_definitions("*program-feed*")
    if results.matches is None or results.matches == "":
        results = []
    else:
        results = results.matches.match

    final_results = []

    # publish all results' relationships
    for result in results:
        type = result.type
        id = result.id

        if type == "block" and '/base-assets/' not in result.path.path and '_testing/' not in result.path.path:
            try:
                relationships = list_relationships(id, type)
                pages = relationships.subscribers.assetIdentifier
                pages_added = []
                for page in pages:
                    resp = publish(page.id, "page", destination)
                    if 'success = "false"' in str(resp):
                        message = resp['message']
                    else:
                        message = 'Published'
                    pages_added.append({'id': page.id, 'path': page.path.path, 'message': message})
            except:
                continue

            final_results.append({'id': result.id, 'path': result.path.path, 'pages': pages_added})

    return render_template('publish-program-feeds-table.html', **locals())


@admin_blueprint.route(publish_manager + '/search', methods=['post'])
def publish_search():
    name = request.form['name']
    content = request.form['content']
    metadata = request.form['metadata']

    # test search info
    results = search(name, content, metadata)
    if results.matches is None or results.matches == "":
        results = []
    else:
        results = results.matches.match

    final_results = []
    for result in results:
        if result.path.siteName == "Public" and (not re.match("_", result.path.path) or re.match("_shared-content", result.path.path) or re.match("_homepages", result.path.path) ):
            final_results.append(result)

    results = final_results
    return render_template('publish-table.html', **locals())

@admin_blueprint.route(publish_manager + '/publish/<destination>/<type>/<id>', methods=['get', 'post'])
def publish_publish(destination, type, id):
    if destination != "staging":
        destination = ""

    if type == "block":
        try:
            relationships = list_relationships(id, type)
            pages = relationships.subscribers.assetIdentifier
            for page in pages:
                if page.type == "page":
                    resp = publish(page.id, "page", destination)
            if 'success = "false"' in str(resp):
                return resp['message']
        except:
            return "Failed"
    else:
        resp = publish(id, type, destination)
        if 'success = "false"' in str(resp):
            return resp['message']

    return "Publishing. . ."

@admin_blueprint.route(publish_manager + "/more_info", methods=['post'])
def publish_more_info():
    type = request.form['type']
    id = request.form['id']

    resp = read(id, type)

    # page
    if type == 'page':
        try:
            info = resp.asset.page
            md = info.metadata
            ext = 'php'
        except:
            return "Not a valid type. . ."
    # block
    elif type == 'block':
        try:
            info = resp.asset.xhtmlDataDefinitionBlock
            md = info.metadata
            ext = ""
        except:
            return "Not a valid type. . ."
    # Todo: file
    else:
        return "Not a valid type. . ."

    # name
    if info.name:
        name = info.name
    # title
    if md.title:
        title = md.title
    # path
    if info.path:
        path = info.path

        if ext != "":
            try:
                www_publish_date = 'N/A'
                staging_publish_date = 'N/A'
                # prod
                # www publish date
                page3 = urllib.urlopen("https://www.bethel.edu/" + path + '.' + ext).read()
                soup3 = BeautifulSoup(page3)
                date = soup3.findAll(attrs={"name":"date"})
                if date:
                    www_publish_date = convert_meta_date(date)

                # staging
                page3 = urllib.urlopen("https://staging.bethel.edu/" + path + '.' + ext).read()
                soup3 = BeautifulSoup(page3)
                date = soup3.findAll(attrs={"name":"date"})
                if date:
                    staging_publish_date = convert_meta_date(date)

            except:
                www_publish_date = 'N/A'
                staging_publish_date = 'N/A'
    # description
    if md.metaDescription:
        description = md.metaDescription

    return render_template("publish-more-info.html", **locals())

def convert_meta_date(date):
    dates = date[0]['content'].encode('utf-8').split(" ")
    dates.pop()
    date = " ".join(dates)

    dt = datetime.datetime.strptime(date, "%a, %d %b %Y %H:%M:%S")
    date_time = datetime.datetime.strftime(dt, "%B %e, %Y at %I:%M %p")

    return date_time

# Code to publish all pages that contain a wufoo block
#
# @publish_blueprint.route('/wufoo', methods=['get'])
# def publish_wufoo():
#     wufoos = search('*wufoo*')
#     for wufoo in wufoos.matches.match:
#         if wufoo.type == "block":
#             relationships = list_relationships(wufoo.id, "block")
#             if 'subscribers' in relationships and 'assetIdentifier' in relationships.subscribers:
#                 for page in relationships.subscribers.assetIdentifier:
#                     publish(page.id, "page")
#
#     return "yep"
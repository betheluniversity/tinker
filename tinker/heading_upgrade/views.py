__author__ = 'ejc84332'

# python

# flask
from flask import Blueprint

# tinker
from tinker.web_services import *
from tinker.cascade_tools import escape_wysiwyg_content

heading_upgrade = Blueprint('heading_upgrade_o', __name__, template_folder='templates')


def upgrade_content(content):
    """
    h3->h2
    h4->h3
    h5->h4
    """
    if not content:
        return ""
    content = content.replace("<h3", "<h2").replace("</h3>", "</h2>")
    content = content.replace("<h4", "<h3").replace("</h4>", "</h3>")
    content = content.replace("<h5", "<h4").replace("</h5>", "</h4>")

    content = content.replace("<h2><strong>", "<h2>").replace("</strong></h2>", "</h2>")
    content = content.replace("<h3><strong>", "<h3>").replace("</strong></h3>", "</h3>")
    content = content.replace("<h4><strong>", "<h4>").replace("</strong></h4>", "</h4>")

    return escape_wysiwyg_content(content)


def log_id_to_file(file_id):
    with open("/opt/tinker/tinker/upgrade.txt", "a") as id_file:
        id_file.write(file_id + "\n")


def submit_upgrade_edit(asset):
    resp = edit(asset)
    if resp['success'] == "true":
        ret = "Upgraded page %s" % asset['page']['path']
        log_id_to_file(asset['page']['id'])
    else:
        ret = "Failed it upgrade page %s" % asset['page']['path']

    return ret


def upgrade_basic_page(page):
    try:
        content = page['asset']['page']['structuredData']['structuredDataNodes']['structuredDataNode'][0]['text']
    except:
        # no data
        return ""
    new_content = upgrade_content(content)
    page['asset']['page']['structuredData']['structuredDataNodes']['structuredDataNode'][0]['text'] = new_content
    asset = {
        'page': page['asset']['page']
    }
    resp = submit_upgrade_edit(asset)
    return resp


def traverse_data_nodes(nodes):
    # Only use this for basic+ type pages
    for node in nodes['structuredDataNode']:
        # check the text
        if node['text']:
            node['text'] = upgrade_content(node['text'])
        # check the child nodes
        if node['structuredDataNodes']:
            traverse_data_nodes(node['structuredDataNodes'])


def upgrade_complex_page(page):

    try:
        content = page['asset']['page']['structuredData']['structuredDataNodes']['structuredDataNode']
    except:
        # no data
        return ""

    for node in content:
        # do the outer "text" entry.
        if node['text']:
            node['text'] = upgrade_content(node['text'])
        if node['structuredDataNodes']:
            traverse_data_nodes(node['structuredDataNodes'])
    asset = {
        'page': page['asset']['page']
    }
    resp = submit_upgrade_edit(asset)
    return resp


def inspect_folder(folder_id):
    folder = read(folder_id, type="folder")
    if not folder:
        yield ""
    children = folder['asset']['folder']['children']
    if not children:
        yield ""
    else:
        for child in children['child']:
            if child['type'] == 'page':
                for item in inspect_page(child['id']):
                    yield item
            elif child['type'] == 'folder':
                yield "looking in folder %s" % child['path']['path']
                for item in inspect_folder(child['id']):
                    yield item


def inspect_page(page_id):
    page = read(page_id)
    page_type = page['asset']['page']['contentTypePath']
    check_id = check_page_id(page['asset']['page']['id'])
    if check_id:
        resp = "skipping page %s because of duplicate id" % page['asset']['page']['path']
    elif page_type == "Basic":
        resp = upgrade_basic_page(page)
    elif page_type.startswith("Basic Plus"):
        # return str(page)
        resp = upgrade_complex_page(page)
    elif page_type.startswith("Event"):
        resp = upgrade_complex_page(page)

    try:
        if not resp:
            resp = "skipping page type %s with id %s" % (page_id, page_type)
        yield str(resp)
    except:
        yield ""


def check_page_id(page_id):

    with open("/opt/tinker/tinker/upgrade.txt") as data:
        page_ids = (line.rstrip('\n') for line in data)
        return page_id in page_ids


def log_message_to_file(message):
    with open("/opt/tinker/tinker/upgrade.txt", "a") as id_file:
        id_file.write(message + "\n")


@heading_upgrade.route('/<start_folder_id>')
def show(start_folder_id):
    # for page in pages:
    #     data = read_path('_testing/jmo/test-page')

    for message in inspect_folder(start_folder_id):
        log_message_to_file(message)

    return "done"


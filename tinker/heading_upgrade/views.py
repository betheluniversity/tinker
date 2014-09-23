__author__ = 'ejc84332'

#python

from flask import Blueprint

from tinker.web_services import *


heading_upgrade = Blueprint('heading_upgrade', __name__,
                               template_folder='templates')

def upgrade_content(content):
    """
    h3->h2
    h4->h3
    h5->h4
    """
    content = content.replace("<h3>", "<h2>").replace("</h3>", "</h2>")
    content = content.replace("<h4>", "<h3>").replace("</h4>", "</h3>")
    content = content.replace("<h5>", "<h4>").replace("</h5>", "</h4>")
    return content


def upgrade_basic_page(page):
    content = page['asset']['page']['structuredData']['structuredDataNodes']['structuredDataNode'][0]['text']
    new_content = upgrade_content(content)

    page['asset']['page']['structuredData']['structuredDataNodes']['structuredDataNode'][0]['text'] = new_content
    asset = {
        'page': page['asset']['page']
    }
    resp = edit(asset)
    return resp


def upgrade_basic_plus_page(page):
    content = page['asset']['page']['structuredData']['structuredDataNodes']['structuredDataNode']
    x = 1


def inspect_folder(folder_id):

    folder = read(folder_id, type="folder")
    children = folder['asset']['folder']['children']['child']
    resp = []
    for child in children:
        if child['type'] == 'page':
            resp.append(inspect_page(child['id']))
            break
        elif child['type'] == 'folder':
            resp.append(inspect_folder(child['id']))

    return "<pre>" + "\n".join(resp) + "</pre>"


def inspect_page(page_id):
    page = read(page_id)
    page_type = page['asset']['page']['contentTypePath']
    if page_type == "Basic":
        upgrade_basic_page(page)
    elif page_type == "Basic Plus":
        return str(page)
        upgrade_basic_plus_page(page)

    return None

@heading_upgrade.route('/')
def show():

    start_folder_id = '221eb5918c58651326c0f0dfe69e3c6d'
    # for page in pages:
    #     data = read_path('_testing/jmo/test-page')

    resp = inspect_folder(start_folder_id)

    return resp
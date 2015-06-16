from tinker import app
import base64

def dynamic_field(name, values):

    values_list = []
    for value in values:
        values_list.append({'value': value})
    node = {
        'name': name,
        'fieldValues': {
            'fieldValue': values_list,
        },
    }

    return node


def structured_data_node(node_id, text, node_type=None):

    if not node_type:
        node_type = "text"

    node = {

        'identifier': node_id,
        'text': text,
        'type': node_type,
    }

    return node


def structured_file_data_node(node_id, path, asset_type="file"):

    node = {
        'identifier': node_id,
        'filePath': path,
        'assetType': asset_type,
        'type': "asset"
    }
    return node


# Excape content so its Cascade WYSIWYG friendly
# There are a few edge cases for sybmols it doesn't like.
def escape_wysiwyg_content(content):
    if content:
        uni = HTMLEntitiesToUnicode(content)
        htmlent = unicodeToHTMLEntities(uni)
        return htmlent
    else:
        return None


# from:
# http://stackoverflow.com/questions/701704/convert-html-entities-to-unicode-and-vice-versa
from BeautifulSoup import BeautifulStoneSoup
import cgi


def HTMLEntitiesToUnicode(text):
    """Converts HTML entities to unicode.  For example '&amp;' becomes '&'."""
    text = unicode(BeautifulStoneSoup(text, convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
    return text


def unicodeToHTMLEntities(text):
    """Converts unicode to HTML entities.  For example '&' becomes '&amp;'."""
    text = cgi.escape(text).encode('ascii', 'xmlcharrefreplace')
    return text
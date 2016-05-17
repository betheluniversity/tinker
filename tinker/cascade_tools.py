from tinker import app
import base64

# todo where should this go?
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

# todo where should this go?
def structured_data_node(node_id, text, node_type=None):

    if not node_type:
        node_type = "text"

    node = {

        'identifier': node_id,
        'text': text,
        'type': node_type,
    }

    return node

# todo where should this go?
def structured_file_data_node(node_id, path, asset_type="file"):

    node = {
        'identifier': node_id,
        'filePath': path,
        'assetType': asset_type,
        'type': "asset"
    }
    return node


# todo move
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

# todo move(?)
def HTMLEntitiesToUnicode(text):
    """Converts HTML entities to unicode.  For example '&amp;' becomes '&'."""
    text = unicode(BeautifulStoneSoup(text, convertEntities=BeautifulStoneSoup.ALL_ENTITIES))
    return text

# todo move(?)
def unicodeToHTMLEntities(text):
    """Converts unicode to HTML entities.  For example '&' becomes '&amp;'."""
    text = cgi.escape(text).encode('ascii', 'xmlcharrefreplace')
    return text
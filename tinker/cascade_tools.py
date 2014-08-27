#escape tool
from xml.sax.saxutils import escape

def dynamic_field(name, values):

    values_list = []
    for value in values:
        values_list.append({'value': value})
    node = {
        'name': name,
        'fieldValues': {
            'fieldValue': values_list,
        },
    },

    return node


def structured_data_node(id, text, node_type=None):

    if not node_type:
        node_type = "text"

    node = {

        'identifier': id,
        'text': text,
        'type': node_type,
    }

    return node


## This is pretty crazy. We need to escape the WYSIWYG content, since
## Cascade unescapes the content it receives. We then have to remove the
## escaped non-breaking whitespace ( &amp;nbsp; ).
def escape_wysiwyg_content(content):

    content = escape(content)

    content = content.replace('&amp;nbsp;', ' ')

    return content


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


## Excape content so its Cascade WYSIWYG friendly
## There are a few edge cases for sybmols it doesn't like.
def escape_wysiwyg_content(content):

    content = content.replace("&rsquo;", "&#39;")
    content = content.replace("&nbsp;", " ")
    content = escape(content)

    return content



from cascade_web_services import app

#local

from tools import get_client


def delete(page_id):

    client = get_client()

    identifier = {
        'id': page_id,
        'type': 'page',
    }

    auth = app.config['CASCADE_LOGIN']

    response = client.service.delete(auth, identifier)
    ## Publish the XML so the event is gone
    publish(app.config['EVENT_XML_ID'])
    return response


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


def event_date(start, end, all_day=False):

    list = [
        structured_data_node("start-date", start),
        structured_data_node("end-date", end),
        ]
    if all_day:
        list.append(structured_data_node("all-day", "::CONTENT-XML-CHECKBOX::Yes"))

    node = {
        'type': "group",
        'identifier': "event-dates",
        'structuredDataNodes': {
            'structuredDataNode': list,
        },
    },

    return node

def publish(id):

    client = get_client()

    publishinformation = {
        'identifier': {
            'id': id,
            'type': 'page'
        }
    }

    auth = app.config['CASCADE_LOGIN']

    response = client.service.publish(auth, publishinformation)

    return str(response)


def read(read_id, type="page"):

    client = get_client()

    identifier = {
        'id': read_id,
        'type': type
    }


    auth = app.config['CASCADE_LOGIN']

    response = client.service.read(auth, identifier)

    return response
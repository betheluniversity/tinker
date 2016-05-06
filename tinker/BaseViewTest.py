__author__ = 'ces55739'

from flask import Blueprint, render_template, session
import datetime

from tinker.BaseView import BaseView

BaseViewTestBlueprint = Blueprint('base_view_test', __name__, template_folder='e_announcements/templates')


class BaseViewTestView(BaseView):

    def index(self):
        forms = []
        username = session['username']
        username = 'cerntson'

        # Todo: change this username to be the E-Announcement group
        if username == 'cerntson':
            forms = self.traverse_xml(traverse_xml_callback_func, 'http://staging.bethel.edu/_shared-content/xml/e-announcements.xml')
        else:
            forms = self.traverse_xml(traverse_xml_callback_func, 'http://staging.bethel.edu/_shared-content/xml/e-announcements.xml', username)

        forms.sort(key=lambda item:item['first_date'], reverse=True)
        forms = reversed(forms)
        return render_template('e-announcements-home.html', **locals())


# Todo: just have to write the logic here to finish it out
def traverse_xml_callback_func(child, username):
    author = child.find('author').text

    first = child.find('system-data-structure/first-date').text
    second = child.find('system-data-structure/second-date').text
    first_date_object = datetime.datetime.strptime(first, '%m-%d-%Y')
    first_date = first_date_object.strftime('%A %B %d, %Y')
    first_date_past = first_date_object < datetime.datetime.now()

    second_date = ''
    second_date_past = ''
    if second:
        second_date_object = datetime.datetime.strptime(second, '%m-%d-%Y')
        second_date = second_date_object.strftime('%A %B %d, %Y')
        second_date_past = second_date_object < datetime.datetime.now()

    roles = []
    values = child.find('dynamic-metadata')
    for value in values:
        if value.tag == 'value':
            roles.append(value.text)

    message = ''
    message = recurse(child.find('system-data-structure/message'))

    try:
        workflow_status = child.find('workflow').find('status').text
    except AttributeError:
        workflow_status = None

    page_values = {
        'author': author,
        'id': child.attrib['id'] or "",
        'title': child.find('title').text or None,
        'created-on': child.find('created-on').text or None,
        'first_date': first_date,
        'second_date': second_date,
        'message': message,
        'roles': roles,
        'workflow_status': workflow_status,
        'first_date_past': first_date_past,
        'second_date_past': second_date_past
    }
    return page_values


def recurse(node):
    return_string = ''
    for child in node:
        child_text = ''
        if child.text:
            child_text = child.text

        # recursively renders children
        try:
            if child.tag == 'a':
                return_string += '<%s href="%s">%s%s</%s>' % (child.tag, child.attrib['href'], child_text, recurse(child), child.tag)
            else:
                return_string += '<%s>%s%s</%s>' % (child.tag, child_text, recurse(child), child.tag)
        except:
            # gets the basic text
            if child_text:
                if child.tag == 'a':
                    return_string += '<%s href="%s">%s</%s>' % (child.tag, child.attrib['href'], child_text, child.tag)
                else:
                    return_string += '<%s>%s</%s>' % (child.tag, child_text, child.tag)

        # gets the text that follows the children
        if child.tail:
            return_string += child.tail

    return return_string

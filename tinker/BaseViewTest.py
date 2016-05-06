__author__ = 'ces55739'

from flask import Blueprint

from tinker.BaseView import BaseView

BaseViewTestBlueprint = Blueprint('base_view_test', __name__, template_folder='templates')


class BaseViewTestView(BaseView):

    def index(self):
        self.traverse_xml(traverse_xml_callback_func, 'http://staging.bethel.edu/_shared-content/xml/e-announcements.xml')

    def caleb_test(self):
        return 'test'


# just have to write the logic here to finish it out
def traverse_xml_callback_func(child, username):
    # first = child.find('system-data-structure/first-date').text
    # second = child.find('system-data-structure/second-date').text
    # first_date_object = datetime.datetime.strptime(first, '%m-%d-%Y')
    # first_date = first_date_object.strftime('%A %B %d, %Y')
    # first_date_past = first_date_object < datetime.datetime.now()
    #
    # second_date = ''
    # second_date_past = ''
    # if second:
    #     second_date_object = datetime.datetime.strptime(second, '%m-%d-%Y')
    #     second_date = second_date_object.strftime('%A %B %d, %Y')
    #     second_date_past = second_date_object < datetime.datetime.now()
    #
    # roles = []
    # values = child.find('dynamic-metadata')
    # for value in values:
    #     if value.tag == 'value':
    #         roles.append(value.text)
    #
    # message = ''
    # message = recurse(child.find('system-data-structure/message'))
    #
    # try:
    #     workflow_status = child.find('workflow').find('status').text
    # except AttributeError:
    #     workflow_status = None
    #
    # page_values = {
    #     'author': author,
    #     'id': child.attrib['id'] or "",
    #     'title': child.find('title').text or None,
    #     'created-on': child.find('created-on').text or None,
    #     'first_date': first_date,
    #     'second_date': second_date,
    #     'message': message,
    #     'roles': roles,
    #     'workflow_status': workflow_status,
    #     'first_date_past': first_date_past,
    #     'second_date_past': second_date_past
    # }
    page_values = None
    return page_values


BaseViewTestView.register(BaseViewTestBlueprint)

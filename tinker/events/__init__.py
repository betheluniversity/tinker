__author__ = 'ejc84332'

from flask.ext.classy import FlaskView
from tinker.admin.Events_Controller import EventsController


class EventsView(FlaskView):

    def __init__(self):
        self.base = EventsController


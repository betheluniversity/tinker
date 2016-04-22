from tinker import app
from flask.ext.classy import FlaskView


class ProgramSearchView(FlaskView):

    def __init__(self):
        pass

    def index(self):
        return "program search index"

    def put(self, tag_id=None):
        return "put tag with id: %s" % tag_id

    def delete(self, tag_id=None):
        return "delete tag with id: %s" % tag_id

    def get(self, tag_id=None):
        return "get tag with id: %s" % tag_id

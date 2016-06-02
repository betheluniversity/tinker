
from flask import abort

from tinker import tools
from tinker.tinker_controller import TinkerController

class RedirectsController(TinkerController):

    def check_redirect_groups(self):
        groups = tools.get_groups_for_user()
        if 'Tinker Redirects' not in groups:
            abort(403)


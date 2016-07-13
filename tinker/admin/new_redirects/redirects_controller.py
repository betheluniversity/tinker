from flask import abort

from tinker import tools, app
from tinker.tinker_controller import TinkerController
# from tinker.redirects.models import BethelRedirect

class RedirectsController(TinkerController):

   def check_redirect_groups(self):
       groups = tools.get_groups_for_user()
       if 'Tinker Redirects' not in groups:
           abort(403)

   def create_redirect_text_file(self):
       map_file = open(app.config['REDIRECT_FILE_PATH'], 'w')
       map_file_back = open(app.config['REDIRECT_FILE_PATH'] + ".back", 'w')
       # redirects = BethelRedirect.query.all()

       # for item in redirects:
       #     map_file.write("%s %s\n" % (item.from_path, item.to_url))
       #     map_file_back.write("%s %s\n" % (item.from_path, item.to_url))
       #
       resp = 'done'
       return resp
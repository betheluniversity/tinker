from tinker import app, db
from tinker.tinker_controller import TinkerController
from tinker.redirects.models import BethelRedirect


class RedirectsController(TinkerController):
    # Creates a new redirect text file
    def create_redirect_text_file(self):
        map_file = open(app.config['REDIRECT_FILE_PATH'], 'w')
        map_file_back = open(app.config['REDIRECT_FILE_PATH'] + ".back", 'w')
        redirects = BethelRedirect.query.all()

        for item in redirects:
            map_file.write("%s %s\n" % (item.from_path, item.to_url))
            map_file_back.write("%s %s\n" % (item.from_path, item.to_url))

        resp = 'done'
        return resp

    # Adds the redirect to the database
    def database_add(self, redirect):
        db.session.add(redirect)
        db.session.commit()

    # Deletes the redirect to the database
    def database_delete(self, redirect):
        db.session.delete(redirect)
        db.session.commit()

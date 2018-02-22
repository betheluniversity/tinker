from flask import render_template, session, request, Blueprint
from flask_classy import FlaskView, route

from tinker.tinker_controller import admin_permissions, EncodingDict

# solution from here: https://stackoverflow.com/questions/1617078/ordereddict-for-older-versions-of-python
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


# doesnt work locally, tinker not accepting local cookies
class UserRolesView(FlaskView):
    route_base = '/admin/user_roles'

    def __init__(self):
        pass

    def before_request(self, name, **kwargs):
        if 'session_clear' not in request.path:
            admin_permissions(self)

    def index(self):
        return render_template('admin/user-roles/home.html', **locals())

    @route('/test_roles_and_users_submit', methods=['POST'])
    def test_roles_and_users_submit(self):
        if 'admin_username' in session.keys():
            current_username = session['admin_viewer_username']
        else:
            current_username = session['username']

        # get username
        rform = EncodingDict(request.form)  # When this module gets a controller,
        username = rform.get('username')    # replace EncodingDict() with self.base.dictionary_encoder.encode()

        if username:
            session.clear()
            # session_keys = copy.deepcopy(session.keys())
            # for key in session_keys:
            #     session.pop(key)

            session['admin_username'] = current_username
            session['username'] = username
        else:
            return 'error'

        session['admin_viewer'] = True

        # session.modified = True
        return '/'  # have the JS handle where we go (homepage)

    @route('/session_clear', methods=['POST'])
    def session_clear(self):
        session.clear()

        return 'success'

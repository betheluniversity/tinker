__author__ = 'ejc84332'

from flask import request
from flask import session
from flask import json as fjson
import requests

class TinkerTools():

    def __init__(self, config):
        self.config = config

    def get_user(self):

        if self.config['ENVIRON'] == 'prod':
            username = request.environ.get('REMOTE_USER')
        else:
            username = self.config['TEST_USER']
            session['username'] = username
            self.get_roles(username)

	if 'roles' not in session.keys():
	    self.get_roles(username)
        
        return username

    def get_groups_for_user(self, username=None):
        from web_services import read
        if not username:
            username = self.get_user()
        user = read(username, "user")
        allowed_groups = user.asset.user.groups
        return allowed_groups.split(";")

    def get_roles(self, username):
        url = self.config['API_URL'] + "/username/%s/roles" % username
        r = requests.get(url, auth=(self.config['API_USERNAME'], self.config['API_PASSWORD']))
        roles = fjson.loads(r.content)
        ret = []
        for key in roles.keys():
            ret.append(roles[key]['userRole'])

        ## Manually give 'faculty' privileges.
        #todo lets move this to a cascade group
        #if username == 'ejc84332':
        #    ret.append('FACULTY')
        if username == 'ces55739':
            ret.append('FACULTY')
        if username == 'celanna':
            ret.append('FACULTY')

        session['roles'] = ret

        return ret



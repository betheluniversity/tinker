from flask import Blueprint, render_template
from flask_classy import FlaskView, route

from bu_cascade.cascade_connector import Cascade

from tinker.tinker_controller import admin_permissions


class UserRolesView(FlaskView):
    route_base = '/admin/user-roles'

    def before_request(self, args):
        admin_permissions(self, 'route_base', args)

    def index(self):
        return render_template('', **locals())  # make .html to return

    def test_roles_and_user(self):
        # TODO inhabit this method
        # same as portal, just use that as template
        # add config variables to config file

    @route('/test_roles_and_users_submit/', methods=['POST'])
    def test_roles_and_users_submit(self):
        # TODO inhabit this method
        # same as portal, just use that as template

    @route('/test_roles_and_users_remove/')
    def test_roles_and_users_remove(self):
        # TODO inhabit this method
        # same as portal, use that as template
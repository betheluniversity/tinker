from flask import Blueprint, render_template, session, redirect, request
from flask_classy import FlaskView, route

from bu_cascade.cascade_connector import Cascade

from tinker.tinker_controller import admin_permissions

from tinker import app


def test_roles_and_user(self):
    cascade_connection = Cascade(app.config['SOAP_URL'],{'username': app.config['AUTH_USERNAME'], 'password': app.config['AUTH_PASSWORD']},
                                     app.config['SITE_ID'], app.config['STAGING_DESTINATION_ID'])
    role_asset = cascade_connection.read(app.config['CASCADE_MD_ROLES_ID'], 'metadataset')
    role_data = role_asset['asset']['metadataSet']['dynamicMetadataFieldDefinitions']['dynamicMetadataFieldDefinition']

    cascade_md_roles = {}
    for item in role_data:
        try:
            cascade_md_roles[item['name']] = item['possibleValues']['possibleValue']
        except:
            continue

    return render_template('admin/test_roles_and_users.html', **locals())


class AdminView:

    def __init__(self):
        pass

    @route('/test_roles_and_users_submit/', methods=['POST'])
    def test_roles_and_users_submit(self):
        if 'admin_username' in session.keys():
            current_username = session['admin_viewer_username']
        else:
            current_username = session['username']

        # get roles
        role = request.form.get('role')
        # get username
        username = request.form.get('username')

        # Todo: the main problem with doing role based checks, is some channels require a username
        # Todo: also, things like the profile image are up in the air. do we show the user's image? or hide it.
        if role:
            # set user_roles and clear user_tabs
            session['admin_viewer_role'] = role
            session['user_roles'] = [role]
            session.pop('user_tabs')
        elif username:
            session.clear()
            session['admin_username'] = current_username
            session['username'] = username
        else:
            return 'error'

        session['admin_viewer'] = True
        return '/'  # have the JS handle where we go (homepage)


    @route('/test_roles_and_users_remove/')
    def test_roles_and_users_remove(self):
        session.clear()
        return 'success'
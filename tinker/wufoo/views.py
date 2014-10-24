#python
import json
import requests

#flask
from flask import request, Blueprint, render_template, jsonify

#Tinker
from tinker import db
from tinker import cache
from tinker.wufoo.models import FormInfo
from tinker.wufoo import api

wufoo_blueprint = Blueprint('wufoo', __name__,
                        template_folder='templates', static_folder='static')
@wufoo_blueprint.route("/")
def show_manage():

    forms = api.get_form_list()

    return render_template('index.html', **locals())


@wufoo_blueprint.route('/all-preload')
def all_preload():
    forms = json.loads(get_forms())['Forms']
    url = "https://editor.its.bethel.edu/silva/wufoo/wufoo-manager/++rest++wufoo-preload-info?skip-bethel-auth=1&site=betheluniversity&form=%s"
    username = "wufoo-upgrade"
    password = "password"
    site="betheluniversity"
    ret = []
    for form in forms:
        x = 1
        hash = form['Hash']
        request_url = url % hash
        resp = requests.get(request_url, auth=(username, password))
        preload_info = resp.content
        db_row = FormInfo(hash=hash, preload_info=preload_info, paypal_name=None, paypal_budget_number=None, sync_status=False)
        try:
            db.session.add(db_row)
            db.session.commit()
        except:
            db.session.rollback()
            db.session.merge(db_row)
            db.session.commit()
        ret.append(db_row)
    resp = ""
    for item in ret:
        resp += str(item) + "\n"

    return "<pre>%s</pre>" % resp


@wufoo_blueprint.route("/get-forms") #, methods=['POST'])
@cache.cached(timeout=500)
def get_forms():
    return api.get_form_list()


@wufoo_blueprint.route('/embed-form/<formhash>')
@wufoo_blueprint.route('/embed-form/<formhash>/<username>')
def embed_form(formhash, username=None):
    ##need to check preload if there is a username
    if username:
        ##info = FormInfo.query.get(formhash)
        ##preload = info['preload_info']
        preload_options = "Field218=jameson&Field217=eric&Field216=e-jameson@bethel.edu"
    else:
        preload_options = ""
    ## Get the username?


    return render_template('embed_form.html', **locals())


@wufoo_blueprint.route('/load-form/<formhash>')
def load_form(formhash):

    #Load prelaod info for form
    info = FormInfo.query.get(formhash)

    return api.load_form(formhash, form_info=info)


@wufoo_blueprint.route('/preload-save', methods=['POST'])
def preload_save():
    mappings = request.form
    sync_fields = {}
    form_hash = ''
    form_name = ''
    keys = mappings.keys()
    for key in keys:
        value = mappings[key]
        if key.startswith('Field') and value:
            sync_fields[key] = value
        elif key == 'wufoo-form-hash':
            form_hash, form_name = mappings[key].split(":")

    preload_info = json.dumps(sync_fields)

    ##Check if there is an entry in the DB for this form yet
    dbrecord = FormInfo.query.get(form_hash)

    if dbrecord:
        #update existing
        dbrecord.preload_info = preload_info
        db.session.merge(dbrecord)
        db.session.commit()

    else:
        #create new
        info = FormInfo(hash=form_hash, preload_info=preload_info, paypal_name=None, paypal_budget_number=None, sync_status=False)
        db.session.add(info)
        db.session.commit()
    return "done"

@wufoo_blueprint.route('/get-preload-options')
def get_preload_options():
    supported_names = {
                       'firstName': 'Last Name',
                       'lastName': 'First Name',
                       }

    return jsonify(dict(supported_names))
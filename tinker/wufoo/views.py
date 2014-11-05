#python
import json
import requests

#flask
from flask import request, Blueprint, render_template, jsonify

#Tinker
from tinker import app
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


@wufoo_blueprint.route('/embed-form/<formhash>', methods=['GET', 'POST'])
@wufoo_blueprint.route('/embed-form/<formhash>/<username>', methods=['GET', 'POST'])
def embed_form(formhash, username=None):
    ##need to check preload if there is a username
    if username:
        info = FormInfo.query.get(formhash)
        preload = info.preload_info
        ## get preload values from api

        #check if this thing needs to have a lookup field
        mapping = json.loads(preload)
        lookup = False
        for value in mapping.values():
            if value.endswith('-lookup'):
                lookup = True
                break
        if lookup:
            ##show the lookup form
            ## what to do about the other preload values, if any?
            return render_template('embed_lookup_form.html', **locals())

        preload_options = get_preload_values(preload, username)

    else:
        preload_options = ""
    ## Get the username?
    return render_template('embed_form.html', **locals())


@wufoo_blueprint.route('/embed-lookup-form/<formhash>/<username>/<bid>')
def lookup_embed_form(formhash, bid, username=None):

    ##create preload_options
    info = FormInfo.query.get(formhash)
    preload = info.preload_info
    preload_options = get_preload_values(preload, username)
    preload_options += "&%s" % get_lookup_values(preload, id)

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
    return "Preload Mapping Saved"


@wufoo_blueprint.route('/get-preload-options')
def get_preload_options():
    return jsonify(dict(get_options()))


def call_wsapi(values, search_type, search_param):
    ##values is a set of fields to lookup
    ##search_type is 'username' if search_param is a username,
    ##bethel_id if otherwise
    ##returns a json array of the response.
    options = get_options()
    common = set(options['common'])
    rare = set(options['rare'])

    payload = {'common': values & common, 'rare': values & rare}
    preload_url = app.config['WUFOO_PRELOAD_URL'] % (search_type, search_param)
    r = requests.post(preload_url, data=payload)
    results = json.loads(r.content)
    return results


def get_preload_values(preload, username):
    preload = json.loads(preload)
    values = set(preload.values())

    results = call_wsapi(values, 'username', username)
    resp = ""
    for key, value in preload.items():
        if value == 'referrer':
            try:
                resp += "%s=%s&" % (key, request.form['referrer'])
            except:
                continue
        if value not in results:
            continue
        resp += "%s=%s&" % (key, results[value])

    return resp


def get_lookup_values(preload, bethel_id):

    preload = json.loads(preload)
    values = set(preload.values())

    ##only want to look up values for the "lookup" fields.
    lookup_values = []
    for value in values:
        if value.endswith('-lookup'):
            lookup_values.append(value.replace('-lookup', ''))

    values = set(values)


    results = call_wsapi(values, 'bethel_id', bethel_id)

    ##build the return string
    resp = ""
    for key, value in preload.items():
        #only inspect the lookup options
        if not value.endswith('-lookup'):
            continue
        #it has lookup, but the request results don't, so strip it off now
        value = value.replace('-lookup', '')
        if value not in results:
            continue
        ##if it passes all the checks, add the value to the appropriate field
        resp += "%s=%s&" % (key, results[value])

    return resp


def get_options():
    return {
        'common' : {
           'firstName': 'First Name',
           'lastName': 'Last Name',
           'referrer': 'Referrer',
           'firstName-lookup': 'First Name - Lookup',
           'lastName-lookup': 'Last Name - Lookup'
        },
       'rare':  {
            'GS Summer 15 Credit': 'Summer15CreditGS'
        }
    }
### methods to interact directly with the wufoo api
import urllib2
import base64
import urllib
import simplejson
import random

from flask import jsonify

from tinker import app


def get_form_list():

    response = call_api(form='all')
    return response


def load_form(formhash, form_info=None, api='fields'):

    response = call_api(form=formhash, api=api)
    if form_info:
        form_info = form_info.serialize()

    return jsonify({"form": response, "info": form_info})


def call_api(form, api='forms', format='json', extra_params={}, unquote_plus=False):
    params = None
    base_url = app.config['WUFOO_BASE_URL']

    if form and form != 'all':
        if api == 'forms':
            #requesting form information for a single form
            # this has a different URL format that the other form apis
            url = base_url + 'api/v3/forms/%s.%s'%(form, format)
        else:
            url = base_url + 'api/v3/forms/%s/%s.%s'%(form, api, format)
    else:
        #e.g. forms api -- to retrieve list of all forms
        url = base_url + 'api/v3/%s.%s'%(api, format)
    if extra_params:
        params = urllib.urlencode(extra_params)
        if unquote_plus:
            #urlencode uses quote_plus(), when extra_params contains a wufoo filter
            #the plus signs can not be encoded
            params = urllib.unquote_plus(params)
        if api != 'webhooks':
            url += '?' + params

    req = urllib2.Request(url)
    keys = app.config['API_KEYS']
    api_key = random.choice(keys)

    authheader = "Basic " + base64.encodestring('%s:%s' % (api_key, 'blastoff'))[:-1]
    req.add_header("Authorization", authheader)
    if api == 'webhooks' and params:
        req.get_method = lambda: 'PUT'
        response = urllib2.urlopen(req, data=params, timeout=10)
    else:
        response = urllib2.urlopen(req, timeout=10)
    return ''.join(response.readlines())

def call_and_load_json(site, form, api, api_key, format='json', extra_params={}, unquote_plus=False):
    r = call_api(site, form, api, api_key, format, extra_params, unquote_plus)
    try:
        return simplejson.loads(r)
    except:
        return r

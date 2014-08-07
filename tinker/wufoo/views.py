#flask
from flask import Blueprint, render_template, jsonify

#Tinker
from tinker import app
from tinker import db
from tinker import cache
from tinker.wufoo.models import FormInfo


import api

wufoo_blueprint = Blueprint('wufoo', __name__,
                        template_folder='templates', static_folder='static')
@wufoo_blueprint.route("/")
def show_manage():

    forms = api.get_form_list()

    return render_template('index.html', **locals())


@wufoo_blueprint.route("/get-forms") #, methods=['POST'])
@cache.cached(timeout=500)
def get_forms():
    return api.get_form_list()


@wufoo_blueprint.route('/load-form/<formhash>')
def load_form(formhash):

    #Load prelaod info for form
    info = FormInfo.query.get(formhash)

    return api.load_form(formhash, form_info=info)


@wufoo_blueprint.route('/get-preload-options')
def get_preload_options():
    supported_names = {'bethel_id': 'Bethel ID',
                       'last_name': 'Last Name',
                       'first_name': 'First Name',
                       'middle_name': 'Middle Name',
                       'bu_email': 'BU Email',
                       'udc_id': 'UDC Id (unique identifier)',
                       'phonetic': 'Phonetic',
                       'majr1': 'Major 1',
                       'majr2': 'Major 2',
                       'majr3': 'Major 3',
                       'majr4': 'Major 4',
                       'majr5': 'Major 5',
                       'department': 'Department',
                       'begtime': 'Ceremony Begin Time',
                       'cermdate': 'Ceremony Date',
                       'CohortUG': 'CAPS Cohort',
                       'CohortGS': 'GS Cohort',
                       'CohortUG1415': 'CAPS Cohort',
                       'CohortGS1415': 'GS Cohort',
                       'Fall13CreditUG': 'CAPS Fall 13 Credit',
                       'Spring14CreditUG': 'CAPS Spring 14 Credit',
                       'Summer14CreditUG': 'CAPS Summer 14 Credit',
                       'Fall13CreditGS': 'GS Fall 13 Credit',
                       'Spring14CreditGS': 'GS Spring 14 Credit',
                       'Summer14CreditGS': 'GS Summer 14 Credit',
                       'Fall14CreditUG': 'CAPS Fall 14 Credit',
                       'Spring15CreditUG': 'CAPS Spring 15 Credit',
                       'Summer15CreditUG': 'CAPS Summer 15 Credit',
                       'Fall14CreditGS': 'GS Fall 14 Credit',
                       'Spring15CreditGS': 'GS Spring 15 Credit',
                       'Summer15CreditGS': 'GS Summer 15 Credit'
                       }

    return jsonify(dict(supported_names))
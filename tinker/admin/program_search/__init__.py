import urllib2
import gspread
import csv
import ast
import json
from xml.etree import ElementTree as ET
from oauth2client.service_account import ServiceAccountCredentials

from flask.ext.classy import FlaskView
from flask import render_template
from flask import Blueprint
from flask import jsonify
from flask import session
from flask import abort
from flask.ext.classy import route, request

from tinker import app, db
from tinker.admin.program_search.models import ProgramTag
from tinker.admin.program_search.program_search_controller import *

ProgramSearchBlueprint = Blueprint("program_search", __name__, template_folder='templates')


class ProgramSearchView(FlaskView):

    def __init__(self):
        pass

    def before_request(self, args):
        # give access to admins and lauren
        if 'Administrators' not in session['groups'] and session['username'] != 'parlau' and session['username'] != 'dmf23632':
            abort(403)

    def index(self):
        school_labels = get_school_labels()
        program_concentrations = get_programs_for_dropdown()

        return render_template('index.html', **locals())

    def post(self):
        school_labels = get_school_labels()
        program_concentrations = get_programs_for_dropdown()

        rform = json.loads(request.data)
        key = rform.get('key')
        tag = rform.get('tag')

        if key == 'Any' or tag == '' or tag is None:
            return render_template('index.html', **locals())

        outcome = ast.literal_eval(rform.get('outcome'))
        topic = ast.literal_eval(rform.get('topic'))
        other = ast.literal_eval(rform.get('other'))

        try:
            program_tag = ProgramTag(key=key, tag=tag, outcome=outcome, other=other, topic=topic)
            session = db.session

            session.add(program_tag)
            session.commit()

            create_new_csv_file()
        except:
            db.session.rollback()

        return render_template('index.html', **locals())

    @route('/multi-delete', methods=['POST'])
    def multi_delete(self):
        ids_to_delete = json.loads(request.data)
        for id in ids_to_delete:
            ProgramTag.query.filter_by(id=id).delete()
        db.session.commit()
        create_new_csv_file()
        return 'done'

    def delete(self, tag_id=None):
        ProgramTag.query.filter_by(id=tag_id).delete()
        db.session.commit()
        create_new_csv_file()
        return "done"

    @route('/search', methods=['post'])
    def search(self):
        data = json.loads(request.data)
        search_tag = data['search_tag']
        search_key = data['search_key']
        search_results = []
        results_from_search_tag = []
        results_from_search_key = []

        # search
        if search_tag:
            results_from_search_tag = ProgramTag.query.filter(ProgramTag.tag.like("%" + search_tag + "%")).all()
        if search_key:
            results_from_search_key = ProgramTag.query.filter(ProgramTag.key.like(search_key + "%")).all()

        # return results
        if search_tag and search_key:
            for result in results_from_search_key:
                if result in results_from_search_tag:
                    search_results.append(result)
        elif search_tag:
            search_results = results_from_search_tag
        elif search_key:
            search_results = results_from_search_key

        # gather the 'Actual name' for each program, instead of concentration code or name of program block.
        # todo: this is a pretty slow process, will need to speed it up.
        program_concentrations = get_programs_for_dropdown()
        actual_search_result = []
        for search_result in search_results:
            actual_name = filter(lambda person: person['value'] == search_result.key, program_concentrations)
            if len(actual_name) > 0:
                if actual_name[0]:
                    search_result.actual_name = actual_name[0]['name']
            else:
                print 'error'
        return render_template('program-search-ajax.html', **locals())

    # This can be commented out once we stop using the csv files
    def process_worksheet(self, worksheet, concentration_code):
        try:
            session = db.session
            rows = worksheet.get_all_values()
            rows.pop(0)
            for row in rows:
                tag, outcome, other, topic = row
                outcome = bool(outcome)
                other = bool(other)
                topic = bool(topic)

                tag = ProgramTag(key=concentration_code, tag=tag, outcome=outcome, other=other, topic=topic)
                session.add(tag)
                session.commit()
        except:
            pass

    # This can be moved to a controller, this needs to be called from delete
    def dump(self):
        create_new_csv_file()

    @route('/audit', methods=['get'])
    @route('/database-audit', methods=['get'])
    def database_audit(self):
        return render_template('database-audit.html', **locals())

    @route('/database-audit-table', methods=['post'])
    def database_audit_table(self):
        # tinker local db
        search_results = ProgramTag.query.distinct('key').group_by('key').all()
        keys_in_tinker_db = []
        for search_result in search_results:
            keys_in_tinker_db.append(search_result.key)

        # cascade block info
            keys_in_cascade = []
        program_concentrations = get_programs_for_dropdown()
        for program_concentration in program_concentrations:
            keys_in_cascade.append(program_concentration.get('value'))

        # get the list of differences
        list_of_issue_programs = list(set(keys_in_tinker_db) - set(keys_in_cascade))

        # get individual differences
        unmatched_keys_in_tinker_db = list(set(list_of_issue_programs) & set(keys_in_tinker_db))
        unmatched_keys_in_cascade = list(set(list_of_issue_programs) & set(keys_in_cascade))

        return render_template('database-audit-table.html', **locals())

    # todo: need to create the 'update' logic.
    @route('/database-audit-update', methods=['post'])
    def database_audit_update(self):
        data = json.loads(request.data)
        old_key = data['old_key']
        new_key = data['new_key']

        if old_key and new_key:
            search_results = ProgramTag.query.filter(ProgramTag.key == old_key).update({'key': new_key})
            db.session.commit()

        return 'DONE'

ProgramSearchView.register(ProgramSearchBlueprint)

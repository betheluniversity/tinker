import urllib2
# import gspread
import csv
import ast
import json
from xml.etree import ElementTree as ET
# from oauth2client.service_account import ServiceAccountCredentials

from flask.ext.classy import FlaskView
from flask import render_template
from flask import Blueprint
from flask import jsonify
from flask import session
from flask import abort
from flask.ext.classy import route, request

from tinker import db
from tinker.admin.program_search.models import ProgramTag
from tinker.admin.program_search.program_search_controller import *

ProgramSearchBlueprint = Blueprint("program_search", __name__, template_folder='templates')


class ProgramSearchView(FlaskView):
    route_base = "/admin/program-search"

    def __init__(self):
        # scope = ['https://spreadsheets.google.com/feeds']
        # path = app.config["GSPREAD_PATH"]
        # credentials = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
        # self.gc = gspread.authorize(credentials)
        pass

    def before_request(self, args, **kwargs):
        if 'groups' not in session:
            # This if statement block has been added for unit testing purposes
            from tinker.tinker_controller import TinkerController
            tc = TinkerController()
            tc.before_request()
        # give access to admins and lauren
        if 'Administrators' not in session['groups'] and session['username'] != 'parlau':
            abort(403)

    def index(self):
        return render_template('index.html')

    @route('/submit', methods=['post'])
    def submit(self):
        rform = request.form
        key = rform.get('key')
        tag = rform.get('tag')
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
            return ""

        return render_template('index.html')

    @route('/delete/<tag_id>', methods=['GET'])
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
            results_from_search_tag = ProgramTag.query.filter(ProgramTag.tag.like(search_tag + "%")).all()
        if search_key:
            results_from_search_key = ProgramTag.query.filter(ProgramTag.key.like(search_key + "%")).all()

        # return results
        if search_tag and search_key:
            for result in results_from_search_key:
                if result in results_from_search_tag:
                    print result.id
                    search_results.append(result)
        elif search_tag:
            search_results = results_from_search_tag
        elif search_key:
            search_results = results_from_search_key

        return render_template('program-search-ajax.html', **locals())

    # This can be commented out once we stop using the csv files
    # def load(self):
    #     """
    #     load all into the DB from google drive.
    #     :return: None
    #     """
    #
    #     # delete all before adding everything back
    #     db.session.query(ProgramTag).delete()
    #     db.session.commit()
    #
    #     response = urllib2.urlopen(app.config['PROGRAMS_XML'])
    #     xml = ET.fromstring(response.read())
    #     program_blocks = xml.findall('.//system-block')
    #
    #     names = []
    #
    #     for block in program_blocks:
    #         name = block.find('name').text
    #         concentrations = block.findall('system-data-structure/concentration')
    #         names.append(name)
    #         for concentration in concentrations:
    #             concentration_code = concentration.find('concentration_code').text
    #             if concentration_code is None:
    #                 concentration_code = name
    #
    #             page = concentration.find('concentration_page')
    #             path = page.find('path').text
    #             if not path or path == '/':
    #                 continue
    #             page_name = path.split('/')[-1]
    #             if page_name in ['index'] and len(concentrations) > 1:
    #                 continue
    #             names.append("\t%s" % page_name)
    #             self.process_sheet(name, page_name, concentration_code)
    #     return "<pre>%s</pre>" % "\n".join(names)
    #
    # # This can be commented out once we stop using the csv files
    # def process_sheet(self, program_name, concentration_name, concentration_code):
    #     try:
    #         drive_file = self.gc.open(program_name)
    #         global_sheet = drive_file.sheet1
    #         self.process_worksheet(global_sheet, concentration_code)
    #         if concentration_name not in ['index']:
    #             concentration_sheet = drive_file.worksheet(concentration_name)
    #             self.process_worksheet(concentration_sheet, concentration_code)
    #     except:
    #         pass
    #
    # # This can be commented out once we stop using the csv files
    # def process_worksheet(self, workseet, concentration_code):
    #     try:
    #         session = db.session
    #         rows = workseet.get_all_values()
    #         rows.pop(0)
    #         for row in rows:
    #             tag, outcome, other, topic = row
    #             outcome = bool(outcome)
    #             other = bool(other)
    #             topic = bool(topic)
    #
    #             tag = ProgramTag(key=concentration_code, tag=tag, outcome=outcome, other=other, topic=topic)
    #             session.add(tag)
    #             session.commit()
    #     except:
    #         pass
    #
    # This can be moved to a controller, this needs to be called from delete
    # def dump(self):
    #     create_new_csv_file()


ProgramSearchView.register(ProgramSearchBlueprint)

import ast
import json

from flask.ext.classy import FlaskView
from flask import Blueprint
from flask import abort
from flask.ext.classy import route

from tinker.admin.program_search.models import ProgramTag
from tinker.admin.program_search.program_search_controller import *

ProgramSearchBlueprint = Blueprint("program_search", __name__, template_folder='templates')


class ProgramSearchView(FlaskView):
    route_base = '/admin/program-search'

    def __init__(self):
        self.base = ProgramSearchController()

    def before_request(self, args):
        # give access to admins and lauren
        if 'Administrators' not in session['groups'] and session['username'] != 'parlau':
            abort(403)

    def index(self):
        school_labels = self.base.get_school_labels()
        program_concentrations = self.base.get_programs_for_dropdown()

        return render_template('program-search-home.html', **locals())

    @route('/submit', methods=['post'])
    def submit(self):
        school_labels = self.base.get_school_labels()
        program_concentrations = self.base.get_programs_for_dropdown()

        rform = json.loads(request.data)
        key = rform.get('key')
        tag = rform.get('tag')

        if key == 'Any' or tag == '' or tag is None:
            return render_template('program-search-home.html', **locals())

        outcome = ast.literal_eval(rform.get('outcome'))
        topic = ast.literal_eval(rform.get('topic'))
        other = ast.literal_eval(rform.get('other'))

        try:
            program_tag = ProgramTag(key=key, tag=tag, outcome=outcome, other=other, topic=topic)
            session = db.session

            session.add(program_tag)
            session.commit()

            self.base.create_new_csv_file()
        except:
            db.session.rollback()

        return render_template('program-search-home.html', **locals())

    @route('/multi-delete', methods=['POST'])
    def multi_delete(self):
        ids_to_delete = json.loads(request.data)
        for id in ids_to_delete:
            ProgramTag.query.filter_by(id=id).delete()
        db.session.commit()
        self.base.create_new_csv_file()
        return 'TEST'

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
        program_concentrations = self.base.get_programs_for_dropdown()
        actual_search_result = []
        for search_result in search_results:
            actual_name = filter(lambda person: person['value'] == search_result.key, program_concentrations)[0]
            if actual_name:
                search_result.actual_name = actual_name['name']
        return render_template('program-search-ajax.html', **locals())

ProgramSearchView.register(ProgramSearchBlueprint)

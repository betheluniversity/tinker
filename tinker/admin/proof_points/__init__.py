import ast
import json

# flask
from flask_classy import FlaskView
from flask import Blueprint
from flask import abort
from flask_classy import route

# tinker
from tinker.admin.proof_points.proof_points_controller import *
from tinker.admin.proof_points import proof_points_controller
from tinker import app

ProofPointsBlueprint = Blueprint("proof_points", __name__, template_folder='templates')


class ProofPointsView(FlaskView):
    route_base = '/admin/proof-points'

    def __init__(self):
        self.base = ProofPointsController()
        self.forms = []
    # def before_request(self, args):
    #     # give access to admins and lauren
    #     if 'Administrators' not in session['groups'] and 'parlau' not in session['groups'] and session['username'] != 'kaj66635':
    #         abort(403)

    def index(self):
        self.forms = self.base.get_forms()
        username = session['username']
        roles = session['roles']
        owners = self.base.gather_dropdown_values_from_key(self.forms, 'owner')
        schools = self.base.gather_dropdown_values_from_key(self.forms, 'school')

        # forms = sorted(forms, key=itemgetter('last-name'), reverse=False)

        return render_template('proof-points-home.html', **locals())

    @route("/filter-points", methods=['post'])
    def filter_points(self):
        if len(self.forms) < 1:
            self.forms = self.base.get_forms()

        filter_data = request.form
        data = self.base.gather_param_data(filter_data)
        filtered_forms = self.base.filter_with_param(self.forms, data)
        count = len(filtered_forms)

        return render_template('filter-results.html', **locals())

    @route("/grab-from-id", methods=['post'])
    def grab_from_id(self):
        if len(self.forms) < 1:
            self.forms = self.base.get_forms()

        id = request.form['id[]']
        form = self.base.return_form_from_id(self.forms, id)

        cms_link = 'https://cms.bethel.edu/entity/open.act?id='"%s"'&type=block&' % id
        # xml_link = 'https://cms.bethel.edu/render/block.act?renderMode=xml&type=block&id='"%s" % id

        # data_xml = self.base.traverse_xml(xml_link, 'proof-point')

        # print data_xml

        # Get values of form
        form_array = {
            'title': form['title'],
            'school': form['school'],
            'owner': form['owner'],
            'path': form['path'],
            'type': form['type'],
            'id': id,
            'cms_link': cms_link}

        if form_array['owner'] == None:
            form_array['owner'] = 'No Owner'

        return json.dumps(form_array)

ProofPointsView.register(ProofPointsBlueprint)

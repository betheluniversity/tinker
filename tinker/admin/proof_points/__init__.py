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

    # def before_request(self, args):
    #     # give access to admins and lauren
    #     if 'Administrators' not in session['groups'] and 'parlau' not in session['groups'] and session['username'] != 'kaj66635':
    #         abort(403)

    def index(self):

        username = session['username']
        roles = session['roles']
        forms = self.base.get_forms_data()
        owners = self.base.gather_dropdown_values_from_key(forms, 'owner')
        schools = self.base.gather_dropdown_values_from_key(forms, 'school')

        # forms = sorted(forms, key=itemgetter('last-name'), reverse=False)

        return render_template('proof-points-home.html', **locals())

    @route("/filter-points", methods=['post'])
    def filter_points(self):  # , name = '', school = '', owner = '', type = 'both'):
        filter_data = request.form
        search_bar = filter_data.get('search-bar')
        school = filter_data.get('school-dropdown')
        owner = filter_data.get('owner-dropdown')
        num_box = filter_data.get('num-box')
        txt_box = filter_data.get('txt-box')

        results = self.base.get_forms_data()
        print 'It went here'
        return "Redirect"

ProofPointsView.register(ProofPointsBlueprint)

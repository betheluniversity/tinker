import ast
import json

# flask
from flask_classy import FlaskView
from flask import Blueprint
from flask import abort
from flask_classy import route

# tinker
from tinker.admin.proof_points.proof_points_controller import *
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

        forms = self.base.traverse_xml(app.config['PROOF_POINTS_XML_URL'], 'system-block')
        # forms = sorted(forms, key=itemgetter('last-name'), reverse=False)

        return render_template('proof-points-home.html', **locals())


ProofPointsView.register(ProofPointsBlueprint)

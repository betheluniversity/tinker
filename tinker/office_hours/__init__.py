# Packages
from flask import Blueprint, render_template, request, session
from flask_classy import FlaskView, route

# tinker
from tinker import app
from tinker.office_hours.forms import OfficeHoursForm
from tinker.office_hours.office_hours_controller import OfficeHoursController


OfficeHoursBlueprint = Blueprint('office_hours', __name__, template_folder='templates')


class OfficeHoursView(FlaskView):
    route_base = '/office-hours'

    def __init__(self):
        self.base = OfficeHoursController()

    def before_request(self, name, **kwargs):
        pass

    def index(self):

        username = session['username']

        forms = self.base.traverse_xml(app.config['OFFICE_HOURS_XML_URL'], 'system-block')

        return render_template('office-hours/home.html', **locals())

    def edit(self, block_id):
        edit_data, sdata, mdata = self.base.load_office_hours_block(block_id=block_id)
        standard_edit_data, s, m = self.base.load_office_hours_block(block_id=app.config['OFFICE_HOURS_STANDARD_BLOCK'])
        
        try:
            edit_data['next_start_date'] = edit_data['next_start_date'].strftime('%m/%d/%Y')
        except:
            pass

        for e in edit_data['exceptions']:
            if e['date']:
                e['date'] = e['date'].strftime('%m/%d/%Y')

        form = OfficeHoursForm(**edit_data)

        return render_template('office-hours/form.html', **locals())

    @route('/submit', methods=['POST'])
    def submit(self):
        rform = request.form
        block_id = rform.get('block_id')

        if block_id:
            block = self.base.read_block(block_id)

            data, mdata, sdata = block.read_asset()
            asset = self.base.update_structure(data, mdata, rform)
            self.base.rotate_hours(asset)

            resp = str(block.edit_asset(asset))
            self.base.cascade_call_logger(locals())
            self.base.log_sentry("Office Hour Submission", resp)

        return render_template('office-hours/confirm.html', **locals())

    def rotate_hours(self, block_id):
        block = self.base.read_block(block_id)
        data, mdata, sdata = block.read_asset()

        self.base.rotate_hours(sdata)
        block.edit_asset(data)
        return 'success'

OfficeHoursView.register(OfficeHoursBlueprint)

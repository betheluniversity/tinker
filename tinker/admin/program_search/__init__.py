import urllib2
import gspread
import csv
from xml.etree import ElementTree as ET
from oauth2client.service_account import ServiceAccountCredentials

from flask.ext.classy import FlaskView
from flask import render_template
from flask import Blueprint
from flask import jsonify

from tinker import app, db
from tinker.admin.program_search.models import ProgramTag

ProgramSearchBlueprint = Blueprint("program_search", __name__, template_folder='templates')


class ProgramSearchView(FlaskView):

    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds']
        path = app.config["GSPREAD_PATH"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(path, scope)
        self.gc = gspread.authorize(credentials)

        # #todo remove this after testing
        # db.session.query(ProgramTag).delete()
        # db.session.commit()

    def index(self):
        return render_template('index.html')

    def put(self, tag_id=None):
        return "put tag with id: %s" % tag_id

    def delete(self, tag_id=None):
        ProgramTag.query.filter_by(id=tag_id).delete()
        db.session.commit()
        return "done"

    def get(self, tag_id=None):

        if tag_id == 'all':
            results = ProgramTag.query.all()
            tags = []
            for tag in results:
                tags.append({
                    'id': tag.id,
                    'key': tag.key,
                    'tag': tag.tag,
                    'outcome': tag.outcome,
                    'topic': tag.topic,
                    'other': tag.other})
            return jsonify({'tags': tags})

        return "get tag with id: %s" % tag_id

    def load(self):
        """
        load all into the DB from google drive.
        :return: None
        """

        response = urllib2.urlopen(app.config['PROGRAMS_XML'])
        xml = ET.fromstring(response.read())
        program_blocks = xml.findall('.//system-block')

        names = []

        for block in program_blocks:
            name = block.find('name').text

            if name not in ['mba-program']:
                continue

            concentrations = block.findall('system-data-structure/concentration')
            names.append(name)
            for concentration in concentrations:
                concentration_code = concentration.find('concentration_code').text
                page = concentration.find('concentration_page')
                path = page.find('path').text
                if not path or path == '/':
                    continue
                page_name = path.split('/')[-1]
                if page_name in ['index']:
                    continue
                names.append("\t%s" % page_name)
                self.process_sheet(name, page_name, concentration_code)
            print name
        return "<pre>%s</pre>" % "\n".join(names)

    def process_sheet(self, program_name, concentration_name, concentration_code):
        drive_file = self.gc.open(program_name)
        global_sheet = drive_file.sheet1
        self.process_worksheet(global_sheet, concentration_code)
        if concentration_name not in ['index']:
            concentration_sheet = drive_file.worksheet(concentration_name)
            self.process_worksheet(concentration_sheet, concentration_code)

    def process_worksheet(self, workseet, concentration_code):
        session = db.session
        rows = workseet.get_all_values()
        rows.pop(0)
        for row in rows:
            tag, outcome, other, topic = row
            outcome = bool(outcome)
            other = bool(other)
            topic = bool(topic)

            tag = ProgramTag(key=concentration_code, tag=tag, outcome=outcome, other=other, topic=topic)
            session.add(tag)
            session.commit()

    def dump(self):
        outfile = open(app.config['PROGRAM_SEARCH_CSV'], 'wb')
        outcsv = csv.writer(outfile)
        rows = []
        records = ProgramTag.query.all()

        for record in records:
            rows.append([record.key, record.tag, record.outcome, record.other, record.topic])

        # # dump column titles (optional)
        # outcsv.writerow(x[0] for x in cursor.description)
        # # dump rows
        #
        #
        outcsv.writerows(iter(rows))
        outfile.close()
        return "<pre>%s</pre>" % str(rows)


ProgramSearchView.register(ProgramSearchBlueprint)
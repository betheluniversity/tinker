import csv

# tinker
from tinker.admin.program_search.models import ProgramTag
from tinker.tinker_controller import *
from tinker import app, db


class ProgramSearchController(TinkerController):

    def create_new_csv_file(self):
        outfile = open(app.config['PROGRAM_SEARCH_CSV'], 'wb')
        outcsv = csv.writer(outfile)
        rows = []
        records = ProgramTag.query.all()
        rows.append(['key', 'tag', 'outcome', 'other', 'topic'])
        for record in records:
            rows.append([record.key, record.tag, record.outcome, record.other, record.topic])

        outcsv.writerows(iter(rows))
        outfile.close()
        return "<pre>%s</pre>" % str(rows)

    def get_programs_for_dropdown(self):
        # gather a list of all program concentrations
        program_concentrations = []

        response = urllib2.urlopen(app.config['PROGRAMS_XML'])
        xml = ET.fromstring(response.read())
        program_blocks = xml.findall('.//system-block')

        for block in program_blocks:
            concentrations = block.findall('system-data-structure/concentration')
            for concentration in concentrations:
                # get name -- create the key used by the db
                concentration_code = concentration.find('concentration_code').text
                if concentration_code is None:
                    concentration_code = block.find('name').text

                program_name = self.get_program_name(block, concentration)

                if program_name is None:
                    continue

                # get school
                school_element = self.search_for_key_in_dynamic_md(block, 'school')
                if hasattr(school_element, 'text'):
                    school = school_element.text
                else:
                    school = None

                program_concentrations.append({
                    'name': program_name,
                    'value': concentration_code,
                    'school': school
                })

        program_concentrations = sorted(program_concentrations, key=lambda k: k['name'])
        return program_concentrations

    def get_program_name(self, block, concentration):
        # get value
        concentration_name = concentration.find('.//concentration_name')
        block_display_name = block.find('displayName')
        block_title = block.find('title')

        if hasattr(concentration_name, 'text') and concentration_name.text:
            program_name = concentration_name.text
        elif hasattr(block_display_name, 'text') and block_display_name.text:
            program_name = block_display_name.text
        elif hasattr(block_title, 'text') and block_title.text:
            program_name = block_title.text
        else:
            return None

        # add in major/minor

        major_or_minor = self.search_for_key_in_dynamic_md(block, 'program-type')
        if hasattr(major_or_minor, 'text') and major_or_minor.text:
            if 'minor' not in program_name.lower() and 'major' not in program_name.lower() and 'program' not in program_name.lower():
                program_name += ' ' + major_or_minor.text

        return program_name

    def get_school_labels(self):
        school_labels = [
            'College of Arts & Sciences',
            'College of Adult & Professional Studies',
            'Graduate School',
            'Bethel Seminary'
        ]
        return school_labels

    # this function is necessary because we don't have python2.7 on the server (we use python2.6)
    def search_for_key_in_dynamic_md(self, block, key_to_find):
        metadata = block.findall("dynamic-metadata")
        for md in metadata:
            if md.find('name').text == key_to_find:
                return md.find('value')
        return None

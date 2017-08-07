import csv

# tinker
from tinker.admin.program_search.models import ProgramTag
from tinker.tinker_controller import *
from tinker import app, db
from operator import itemgetter


class ProofPointsController(TinkerController):

    def inspect_child(self, child, find_all=False):

        # 3) user is in special group -- check school
        # if 'Tinker Faculty Bios - CAS' in groups:
        #     schools_to_check = ['College of Arts and Sciences']
        # elif 'Tinker Faculty Bios - CAPS and GS' in groups:
        #     schools_to_check = ['College of Adult and Professional Studies', 'Graduate School']
        # elif 'Tinker Faculty Bios - SEM' in groups:
        #     schools_to_check = ['Bethel Seminary']
        # else:
        #     schools_to_check = None
        #
        # if schools_to_check:
        #     try:
        #         school_values = []
        #         for school in child.findall('system-data-structure/job-titles/school'):
        #             school_text = school.text
        #             school_values.append(school_text)
        #     except:
        #         school_values = []
        #
        #     for school_value in school_values:
        #         if school_value in schools_to_check:
        #             iterate_proof = True

        try:
            author = child.find('author').text
            author = author.replace(' ', '').split(',')
        except AttributeError:
            author = None

        # get value of bio, if allowed
        try:
            return self._iterate_child_xml(child, author)
        except AttributeError:
            # Todo: remove this print line, once this is tested
            print 'bad'
            return None

    def get_forms(self):
        forms = self.traverse_xml(app.config['PROOF_POINTS_XML_URL'], 'system-block')
        return forms

    def _iterate_child_xml(self, child, author):

        school = None
        for node in child.findall('dynamic-metadata'):
            if node.find('name').text == 'school':
                try:
                    school = node.find('value').text
                except AttributeError:
                    school = 'Other'

        # TODO cleanup the gathering of some of these values
        page_values = {
            'title': child.find('title').text or None,
            'school': school or None,
            'type': child.find('system-data-structure').find('proof-point').find('type').text or None,
            'id': child.attrib['id'] or "",
            'path': 'https://www.bethel.edu' + child.find('path').text or "",
            'owner': child.find('system-data-structure').find('info').find('bethel-owner').text or None,
            'created-on': child.find('created-on') or "",
            'text_before': child.find('system-data-structure').find('proof-point').find('number-group').find('text-before').text or '',
            'number_field': child.find('system-data-structure').find('proof-point').find('number-group').find('number-field').text or '',
            'text_field': child.find('system-data-structure').find('proof-point').find('text').find('main-text').text or '',
            'text_after': child.find('system-data-structure').find('proof-point').find('number-group').find('text-after').text or '',
            'text_below': child.find('system-data-structure').find('proof-point').find('number-group').find('text-below').text or '',
            # If we need to rename the dropdown values, use this below
            # 'name': child.find('name').text or None
        }
        temp = None
        return page_values

    def gather_dropdown_values_from_key(self, forms, key):
        things = []
        for thing in forms:
            things.append(thing[key])
        things_set = set(things)
        things = []
        for thing in things_set:
            if key == "owner" and thing == None:
                thing = "No Owner"
                things.append(thing)
            else:
                things.append(thing)

        things.sort()
        return things

    def gather_param_data(self, filter_data):
        dict = {
            'title': filter_data.get('search-bar'),
            'school': filter_data.get('school-dropdown'),
            'owner': filter_data.get('owner-dropdown'),
        }

        # Small block tests what type is selected
        if filter_data['num-box'] == 'checkbox checked':
            dict['type'] = 'Number'
        elif filter_data['txt-box'] == 'checkbox checked':
            dict['type'] = 'Text'
        else:
            dict['type'] = 'both'

        return dict

    def filter_with_param(self, forms, parameters):
        results = []
        title = parameters['title']
        owner = parameters['owner']
        school = parameters['school']
        type = parameters['type']

        for form in forms:
            # Boolean Check Values - Says 'Do I have to check'
            owner_check = True
            school_check = True
            type_check = True
            # Boolean Match Values - Says 'Do I match'
            title_matches = False
            owner_matches = False
            school_matches = False
            type_matches = False

            if owner == 'any':
                owner_check = False

            if school == 'any':
                school_check = False

            if type == 'both':
                type_check = False

            if title.lower() in form['title'].lower():
                title_matches = True

            if owner_check and form['owner'] == owner:
                owner_matches = True

            if school_check and form['school'] == school:
                school_matches = True

            if type_check and form['type'] == type:
                type_matches = True

            A = title_matches
            B = (not owner_check) or (owner_check and owner_matches)
            C = (not school_check) or (school_check and school_matches)
            D = (not type_check) or (type_check and type_matches)

            if A and B and C and D:
                results.append(form)

        return results

    def return_form_from_id(self, forms, id):
        searched_form = None
        for form in forms:
            if form['id'] == id:
                searched_form = form

        return searched_form

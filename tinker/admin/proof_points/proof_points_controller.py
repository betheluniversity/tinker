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

    def _iterate_child_xml(self, child, author):

        school = None;
        for node in child.findall('dynamic-metadata'):
            if node.find('name').text == 'school':
                school = node.find('value').text

        page_values = {
            'title': child.find('title').text or None,
            'school': school or None,
            'type': child.find('system-data-structure').find('proof-point').find('type').text or None,
            'id': child.attrib['id'] or "",
            'path': 'https://www.bethel.edu' + child.find('path').text or "",
            'owner': child.find('system-data-structure').find('info').find('bethel-owner').text or None,
            'created-on': child.find('created-on') or ""
        }
        temp = None;
        return page_values


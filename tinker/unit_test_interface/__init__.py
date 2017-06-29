import ast
import calendar
import json
import re
import unittest
from cStringIO import StringIO
from datetime import datetime, timedelta

from flask import Blueprint, abort, render_template, stream_with_context, Response
from flask_classy import FlaskView, route
from requests import api as Requests_API

from testing_suite.integration_tests.utilities import get_tests_in_this_dir
from tinker import app

UnitTestBlueprint = Blueprint('UnitTestBlueprint', __name__, template_folder='templates')


def convert_string_to_HTML(string_to_change):
    to_return = ""
    for character in string_to_change:
        if character == "\n":
            to_return += "<br/>"
        elif character == " ":
            to_return += "&nbsp;"
        elif character == "<":
            to_return += "&lt;"
        elif character == ">":
            to_return += "&gt;"
        else:
            to_return += character
    return to_return


def get_travis_api_token():
    url_to_send = "https://api.travis-ci.org/auth/github"
    headers = {
        "User-Agent": "Travis/BU-Tinker/2.0.1",
        "Accept": "application/vnd.travis-ci.2+json",
        "Host": "api.travis-ci.org",
        "Content-Type": "application/json",
        "Content-Length": "37"
    }
    data = {
        "github_token": app.config['GITHUB_TOKEN']
    }
    r = Requests_API.post(url_to_send, json=data, headers=headers)
    r_dict = ast.literal_eval(r.content)
    return r_dict['access_token']


def construct_authorized_post_headers():
    return {
        "Content-Type": "application/json",
        "User-Agent": "Travis/BU-Tinker/2.0.1",
        "Accept": "application/vnd.travis-ci.2+json",
        "Host": "api.travis-ci.org",
        "Authorization": "token " + get_travis_api_token()
    }


def format_date(date_string):
    # Original format: "2016-10-05T16:54:20Z" (ISO 8601 format; Z indicates on UTC +0 time,
    # thus need to adjust to our timezone and then converted to am/pm)
    date_object = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
    timestamp = calendar.timegm(date_object.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    assert date_object.resolution >= timedelta(microseconds=1)
    time_zone_adjusted_date_object = local_dt.replace(microsecond=date_object.microsecond)
    if time_zone_adjusted_date_object.hour > 12:  # P.M.
        time_zone_adjusted_date_object = time_zone_adjusted_date_object - timedelta(hours=12)
        return str(time_zone_adjusted_date_object) + " P.M."
    else:  # A.M.
        if time_zone_adjusted_date_object.hour == 0:
            time_zone_adjusted_date_object = time_zone_adjusted_date_object + timedelta(hours=12)
        return str(time_zone_adjusted_date_object) + " A.M."


class UnitTestInterface(FlaskView):
    route_base = '/unit-test'

    def __init__(self):
        self.travis_api_url = "https://api.travis-ci.org"
        self.travis_get_headers = {
            "User-Agent": "Travis/BU-Tinker/2.0.1",
            "Accept": "application/vnd.travis-ci.2+json",
            "Host": "api.travis-ci.org"
        }

    @route('/', methods=['GET'])
    @route('/<path:module>', methods=['GET'])
    def interface(self, module="all"):
        output = StringIO()
        test_suite_location = app.config['INSTALL_LOCATION'] + "/testing_suite"
        acceptable_modules = ["admin/blink_roles_tests", "admin/cache_tests", "admin/program_search_tests",
                              "admin/publish_tests", "admin/redirects_tests", "admin/sync_tests",
                              "e_announcements_tests", "events_tests", "faculty_bios_tests", "office_hours_tests"]
        if module != "all":
            if module not in acceptable_modules:
                return abort(404)
            test_suite_location += "/" + module
            testsuite = get_tests_in_this_dir(test_suite_location)
            unittest.TextTestRunner(verbosity=1, stream=output).run(testsuite)
            return render_template("base.html", results=convert_string_to_HTML(output.getvalue()))
        else:
            def generator():
                yield "This page will stream the test results as they return.<br/>"
                for module_to_test in acceptable_modules:
                    yield '<h3><a href="/unit-test/' + module_to_test + '">' + module_to_test + '</a></h3>'
                    output = StringIO()
                    testsuite = get_tests_in_this_dir(test_suite_location + "/" + module_to_test)
                    unittest.TextTestRunner(verbosity=1, stream=output).run(testsuite)
                    yield convert_string_to_HTML(output.getvalue())
                yield "End of unit tests"
            return Response(stream_with_context(generator()))

    def dashboard(self):
        modules = ["admin/blink_roles_tests", "admin/cache_tests", "admin/program_search_tests",
                   "admin/publish_tests", "admin/redirects_tests", "admin/sync_tests",
                   "e_announcements_tests", "events_tests", "faculty_bios_tests", "office_hours_tests"]
        return render_template("dashboard.html", modules=modules)

    def travis(self):
        url_to_send = self.travis_api_url + "/repos/betheluniversity/tinker/branches"
        r = Requests_API.get(url_to_send, headers=self.travis_get_headers)
        branches = re.findall("\"branch\":[ ]?\"(.+?)\"", r.content)
        url_to_send = self.travis_api_url + "/repos/betheluniversity/tinker/builds"
        r = Requests_API.get(url_to_send, headers=self.travis_get_headers)
        list_of_builds = r.json()['builds']
        list_of_commits = r.json()['commits']
        info_packets = []
        # Merge the commit information and build information into one packet for render_template simplicity
        for i in range(0, len(list_of_builds)):
            b = list_of_builds[i]
            c = list_of_commits[i]
            # Make sure that the build and commit info match; in theory this should be a redundant check
            if b['commit_id'] == c['id']:
                new_packet = dict()
                new_packet['build_id'] = b['id']
                new_packet['state'] = b['state']
                new_packet['commit'] = c['sha']
                new_packet['branch'] = c['branch']
                new_packet['author'] = c['committer_name']
                new_packet['date'] = format_date(c['committed_at'])
                info_packets.append(new_packet)

        return render_template("travis.html", list_of_info=info_packets, branches=branches)

    def view_travis_build(self, build_id):
        url_to_send = self.travis_api_url + "/builds/" + build_id
        r = Requests_API.get(url_to_send, headers=self.travis_get_headers)
        condensed_packet = dict()
        alias = r.json()
        condensed_packet['commit_id'] = alias['build']['commit_id']
        language = alias['build']['config']['language']
        condensed_packet['language'] = language + " " + alias['build']['config'].get(language, ["0.0.0"])[0]
        condensed_packet['duration'] = alias['build']['duration']
        condensed_packet['event_type'] = alias['build']['event_type']
        condensed_packet['build_id'] = alias['build']['id']
        condensed_packet['repository_id'] = alias['build']['repository_id']
        condensed_packet['state'] = alias['build']['state']
        condensed_packet['author'] = alias['commit']['committer_name']
        condensed_packet['branch'] = alias['commit']['branch']
        condensed_packet['compare_url'] = alias['commit']['compare_url']

        key_order = ['build_id', 'state', 'duration', 'language', 'repository_id', 'commit_id', 'event_type', 'branch',
                     'compare_url', 'author']

        return render_template("travis_build_view.html", order=key_order, packet=condensed_packet)

    def rerun_travis_build(self, build_id):
        url_to_send = self.travis_api_url + "/builds/" + build_id + "/restart"
        r = Requests_API.post(url_to_send, headers=construct_authorized_post_headers())
        return r.content

    @route('/simple-return/<path:module>', methods=['GET'])
    def simpleReturn(self, module):
        test_suite_location = app.config['INSTALL_LOCATION'] + "/testing_suite"
        modules = ["admin/blink_roles_tests", "admin/cache_tests", "admin/program_search_tests",
                   "admin/publish_tests", "admin/redirects_tests", "admin/sync_tests",
                   "e_announcements_tests", "events_tests", "faculty_bios_tests", "office_hours_tests"]
        if module not in modules:
            return abort(404)
        output = StringIO()
        testsuite = get_tests_in_this_dir(test_suite_location + "/" + module)
        unittest.TextTestRunner(verbosity=1, stream=output).run(testsuite)
        result = output.getvalue().split("\n")[0]
        if "F" in result or "E" in result:
            succinct_result = "Fail"
        else:
            succinct_result = "Pass"
        return json.dumps([module, succinct_result, convert_string_to_HTML(output.getvalue())])

UnitTestInterface.register(UnitTestBlueprint)

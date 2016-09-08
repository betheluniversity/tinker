from flask import Blueprint, abort, render_template, stream_with_context, Response
from flask_classy import FlaskView, route

from cStringIO import StringIO
from tinker import app
import json
import unittest

UnitTestBlueprint = Blueprint('UnitTestBlueprint', __name__, template_folder='templates')


def convert_string_to_HTML(string_to_change):
    to_return = ""
    for character in string_to_change:
        if character == "\n":
            to_return += "<br/>"
        elif character == " ":
            to_return += "&nbsp;"
        else:
            to_return += character
    return to_return

class UnitTestInterface(FlaskView):
    route_base = '/unit-test'

    @route('/', methods=['GET'])
    @route('/<path:module>', methods=['GET'])
    def interface(self, module="all"):
        output = StringIO()
        test_suite_location = app.config['INSTALL_LOCATION'] + "/unit_tests"
        acceptable_modules = ["admin/blink_roles_tests", "admin/cache_tests", "admin/program_search_tests",
                              "admin/publish_tests", "admin/redirects_tests", "admin/sync_tests",
                              "e_announcements_tests", "events_tests", "faculty_bios_tests", "office_hours_tests"]

        if module != "all":
            if module not in acceptable_modules:
                return abort(404)
            test_suite_location += "/" + module
            testsuite = unittest.TestLoader().discover(test_suite_location)
            unittest.TextTestRunner(verbosity=1, stream=output).run(testsuite)
            return render_template("base.html", results=convert_string_to_HTML(output.getvalue()))
        else:
            def generator():
                yield "This page will stream the test results as they return.<br/>"
                for module_to_test in acceptable_modules:
                    yield "<h3>" + module_to_test + "</h3>"
                    output = StringIO()
                    testsuite = unittest.TestLoader().discover(test_suite_location + "/" + module_to_test)
                    unittest.TextTestRunner(verbosity=1, stream=output).run(testsuite)
                    yield convert_string_to_HTML(output.getvalue())
                yield "End of unit tests"
            return Response(stream_with_context(generator()))

    def dashboard(self):
        modules = ["admin/blink_roles_tests", "admin/cache_tests", "admin/program_search_tests",
                   "admin/publish_tests", "admin/redirects_tests", "admin/sync_tests",
                   "e_announcements_tests", "events_tests", "faculty_bios_tests", "office_hours_tests"]
        return render_template("dashboard.html", modules=modules)

    @route('/simple-return/<path:module>', methods=['GET'])
    def simpleReturn(self, module):
        test_suite_location = app.config['INSTALL_LOCATION'] + "/unit_tests"
        modules = ["admin/blink_roles_tests", "admin/cache_tests", "admin/program_search_tests",
                   "admin/publish_tests", "admin/redirects_tests", "admin/sync_tests",
                   "e_announcements_tests", "events_tests", "faculty_bios_tests", "office_hours_tests"]
        if module not in modules:
            return abort(404)
        output = StringIO()
        testsuite = unittest.TestLoader().discover(test_suite_location + "/" + module)
        unittest.TextTestRunner(verbosity=1, stream=output).run(testsuite)
        result = output.getvalue().split("\n")[0]
        if "F" in result or "E" in result:
            succinct_result = "Fail"
        else:
            succinct_result = "Pass"
        return json.dumps([module, succinct_result, convert_string_to_HTML(output.getvalue())])

UnitTestInterface.register(UnitTestBlueprint)

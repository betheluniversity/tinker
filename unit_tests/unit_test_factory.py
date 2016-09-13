import os
import sys


def convert_method_name_to_caps(method_name):
    words_in_method_name = method_name.split("_")
    to_return = ""
    for word in words_in_method_name:
        to_return += word.capitalize()
    return to_return


def create_path(path):
    if not os.path.isdir(path):
        if os.path.isfile(path):
            print "This factory is expecting a path to a directory, but you gave it a path to a file"
            sys.exit(1)
        else:
            print "Creating new __init__ in", path
            os.mkdir(path)
            init_contents = """import unittest

if __name__ == "__main__":
    testsuite = unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
"""
            new_init = open(path + "/__init__.py", "w")
            new_init.write(init_contents)
            new_init.close()


def create_get_test(destination_path, method_name, expected_response):
    file_contents = """from unit_tests import BaseTestCase


class %(1)sTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(%(1)sTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request_type = "GET"
        self.request = self.generate_url("%(0)s")

    #######################
    ### Testing methods ###
    #######################

    def test_%(0)s(self):
        expected_response = b'%(2)s'
        response = self.send_get(self.request)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)
""" % {'0': method_name, '1': convert_method_name_to_caps(method_name), '2': expected_response}

    parent_dir = os.path.dirname(os.path.realpath(__file__))
    write_path = parent_dir + "/" + destination_path + "_tests"
    create_path(write_path)
    last_folder = destination_path.split("/")[-1]
    new_test_name = "test_" + last_folder + "_" + method_name + ".py"
    new_test_file = open(write_path + "/" + new_test_name, "w")
    new_test_file.write(file_contents)
    new_test_file.close()
    print "A new GET unit test has been generated for", destination_path + "/" + method_name


def create_post_tests(destination_path, method_name, correct_dict, expected_success_response, expected_failure_response):
    keywords = []
    correct_values = []
    for key, value in correct_dict.iteritems():
        keywords.append(key)
        correct_values.append(value)

    def create_kwargs(list_of_keywords, add_quotes):
        to_return = ""
        for i, kw in enumerate(list_of_keywords):
            if add_quotes:
                to_return += "\"" + kw + "\""
            else:
                to_return += kw
            if i != len(list_of_keywords) - 1:
                to_return += ", "
        return to_return

    def create_dict_internals(list_of_keywords):
        indent = " " * 12
        to_return = ""
        for i, kw in enumerate(list_of_keywords):
            to_return += "\'" + kw + "\': " + kw
            if i != len(list_of_keywords) - 1:
                to_return += ",\n" + indent
        return to_return

    file_contents = """from unit_tests import BaseTestCase


class %(1)sTestCase(BaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def __init__(self, methodName):
        super(%(1)sTestCase, self).__init__(methodName)
        self.class_name = self.__class__.__bases__[0].__name__ + '/' + self.__class__.__name__
        self.request_type = "POST"
        self.request = self.generate_url("%(0)s")

    def create_form(self, %(3)s):
        return {
            %(4)s
        }

    #######################
    ### Testing methods ###
    #######################

    def test_%(0)s_valid(self):
        expected_response = b'%(2)s'
        form_contents = self.create_form(%(5)s)
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)
""" % {'0': method_name, '1': convert_method_name_to_caps(method_name), '2': expected_success_response,
       '3': create_kwargs(keywords, False), '4': create_dict_internals(keywords),
       '5': create_kwargs(correct_values, True)}

    for i, key in enumerate(keywords):
        wrong_values = list(correct_values)
        for j in range(0, len(wrong_values)):
            if j == i:
                wrong_values[j] = "None"
            else:
                wrong_values[j] = "\"" + wrong_values[j] + "\""
        incorrect_kwargs = create_kwargs(wrong_values, False)
        file_contents += """

    def test_%(0)s_invalid_%(1)s(self):
        expected_response = b'%(2)s'
        form_contents = self.create_form(%(3)s)
        response = self.send_post(self.request, form_contents)
        failure_message = self.generate_failure_message(self.request_type, self.request, response.data, expected_response, self.class_name)
        self.assertIn(expected_response, response.data, msg=failure_message)
""" % {'0': method_name, '1': key, '2': expected_failure_response, '3': incorrect_kwargs}

    parent_dir = os.path.dirname(os.path.realpath(__file__))
    write_path = parent_dir + "/" + destination_path + "_tests"
    create_path(write_path)
    last_folder = destination_path.split("/")[-1]
    new_test_name = "test_" + last_folder + "_" + method_name + ".py"
    new_test_file = open(write_path + "/" + new_test_name, "w")
    new_test_file.write(file_contents)
    new_test_file.close()
    print "A new set of POST unit tests have been generated for", destination_path + "/" + method_name


generate_tests = True
if generate_tests:
    create_get_test("admin/blink_roles", "index", '<h2 class="first-subtitle"> Blink Layout Owners </h2>')
    create_get_test("admin/cache", "index", '<input type="text" value="" id="cpath" class="form-control"/>')
    correct_dictionary = {
        'url': "/"
    }
    create_post_tests("admin/cache", "submit", correct_dictionary, "Cache cleared for path,", "400 Bad Request")
    create_get_test("admin/program_search", "index", '<form id=\'program_search_form\' method="post">')
    create_post_tests("admin/program_search", "submit", correct_dictionary, '<form id=\'program_search_form\' method="post">', "400 Bad Request")
    create_post_tests("admin/program_search", "search", correct_dictionary, "class=\"program-search-row table-hover\">", "400 Bad Request")
    create_post_tests("admin/program_search", "multi_delete", correct_dictionary, "Deleted ids:", "400 Bad Request")
    create_get_test("admin/publish", "index", '<img id="img-spinner" src="https://cdn1.bethel.edu/images/load.gif" alt="Loading"/>')
    create_get_test("admin/publish", "publish_program_feeds", '<h3 class="subtitle">Publish Program Feeds</h3>')
    create_get_test("admin/publish", "publish_program_feeds_return", 'Published these pages to')
    create_post_tests("admin/publish", "search", correct_dictionary, "<tr class=\"publish-table\">", "400 Bad Request")
    create_get_test("admin/publish", "publish_publish", 'Publishing. . .')
    create_post_tests("admin/publish", "more_info", correct_dictionary, "<div class=\"col-sm-6 zero-left-padding\">", "400 Bad Request")
    create_get_test("admin/redirects", "index", '<form action="" id="new-redirect-form">')
    create_post_tests("admin/redirects", "delete_redirect", correct_dictionary, "deleted", "fail")
    create_post_tests("admin/redirects", "search", correct_dictionary, '<tr class="redirect-row table-hover" data-reveal-id="confirmModal" data-toggle="modal" data-target="#myModal"', "400 Bad Request")
    create_post_tests("admin/redirects", "new_redirect_submit", correct_dictionary, "deleted", "fail")
    create_get_test("admin/redirects", "compile", '<form action="" id="new-redirect-form">')
    create_get_test("admin/redirects", "expire", 'done')
    # create_post_tests("admin/redirects", "new_api_submit", correct_dictionary, "deleted", "fail")
    # create_post_tests("admin/redirects", "new_api_submit_asset_expiration", correct_dictionary, "deleted", "fail")
    # create_get_test("admin/redirects", "new_internal_redirect_submit", 'done')
    create_get_test("admin/sync", "index", 'You can sync a specific metadata set, data definition, or sync all.')
    create_post_tests("admin/sync", "all", correct_dictionary, "Successfully Synced", "400 Bad Request")
    create_post_tests("admin/sync", "metadata", correct_dictionary, "Successfully Synced", "400 Bad Request")
    create_post_tests("admin/sync", "datadefinition", correct_dictionary, "Successfully Synced", "400 Bad Request")
    create_get_test("e_announcements", "index", 'Below is the list of E-Announcements you have access to edit. These are sorted by')
    create_get_test("e_announcements", "delete", 'Your E-Announcement has been deleted. It will be removed from your')
    create_get_test("e_announcements", "view", '<h5>First Date</h5>')
    create_get_test("e_announcements", "new", '<div class="container-fluid row">')
    create_get_test("e_announcements", "confirm", 'Once your E-Announcement has been approved, it')
    create_get_test("e_announcements", "edit", '<div class="container-fluid row">')
    create_get_test("e_announcements", "duplicate", '<div class="container-fluid row">')
    create_post_tests("e_announcements", "submit", correct_dictionary, "Once your E-Announcement has been approved, it", "400 Bad Request")
    # create_get_test("e_announcements", "create_campaign", '<h5>First Date</h5>')
    create_get_test("e_announcements", "edit_all", 'success')
    create_get_test("events", "index", 'All events will be reviewed and approved within 2-3 business days by Conference')
    create_get_test("events", "confirm", "You'll receive an email when your event has been approved by Conference and Event Services. Once your")
    create_get_test("events", "event_in_workflow", 'Your edits are pending approval. Please wait until they have been approved before you make additional edits.')
    create_get_test("events", "add", 'If you have any questions as you submit your event, please contact Conference and Event Services')
    create_get_test("events", "edit", 'If you have any questions as you submit your event, please contact Conference and Event Services')
    create_get_test("events", "duplicate", 'If you have any questions as you submit your event, please contact Conference and Event Services')
    create_post_tests("events", "submit", correct_dictionary, "You'll receive an email when your event has been approved by Conference and Event Services. Once your", "400 Bad Request")
    # create_get_test("events", "reset_tinker_edits", '')
    create_get_test("events", "edit_all", 'success')
    create_get_test("events", "delete", 'Your event has been deleted. It will be removed from your')
    create_get_test("faculty_bios", "index", "Below is a list of faculty bios you have access to edit. If you don't see your faculty")
    create_get_test("faculty_bios", "delete", 'Your faculty bio has been deleted. It will be removed from your')
    create_get_test("faculty_bios", "delete_confirm", 'Your faculty bio has been deleted. It will be removed from your')
    create_get_test("faculty_bios", "new", '<h3 class="subtitle">Edit Your Bio</h3>')
    create_get_test("faculty_bios", "confirm", '<h1 class="first-subtitle">Congrats!</h1>')
    create_get_test("faculty_bios", "faculty_bio_in_workflow", '')
    create_get_test("faculty_bios", "edit", '<h3 class="subtitle">Edit Your Bio</h3>')
    create_post_tests("faculty_bios", "submit", correct_dictionary, '<h1 class="first-subtitle">Congrats!</h1>',  "400 Bad Request")
    create_post_tests("faculty_bios", "activate", correct_dictionary, "Success", "400 Bad Request")
    create_get_test("faculty_bios", "edit_all", 'success')
    create_get_test("office_hours", "index", 'Below is the list of Office Hours you have access to edit.')
    create_get_test("office_hours", "edit", "Below shows the hours that Bethel University's campus is open along with your office's hours.")
    create_post_tests("faculty_bios", "submit", correct_dictionary, "You've successfully updated your office's hours. You should see these changes reflected ", "400 Bad Request")
    create_get_test("office_hours", "rotate_hours", 'success')
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

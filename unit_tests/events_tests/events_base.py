import inspect
import tinker
import unittest


class EventsBaseTestCase(unittest.TestCase):

    def setUp(self):
        self.verbose_failure = True
        self.app = tinker.app.test_client()

    def send_post(self, url, form_contents):
        result = self.app.post(url, data=form_contents, follow_redirects=True)
        if self.verbose_failure:
            if result._status_code != 200:
                print "\n" + "=" * 50
                print "URL called: ", url
                print "Data sent:", self.pretty_print(form_contents)
                print "Test name:", inspect.stack()[1][3]
                print result
                print "=" * 50
        return result

    def send_get(self, url):
        result = self.app.get(url, follow_redirects=True)
        if self.verbose_failure:
            if result._status_code != 200:
                print "\n" + "=" * 50
                print "URL called: ", url
                print "Test name:", inspect.stack()[1][3]
                print result
                print "=" * 50
        return result

    def pretty_print(self, to_print, indent=0):
        if isinstance(to_print, dict):
            print indent * "    " + "{"
            for key in to_print:
                print (indent+1) * " " + key + ":"
                self.pretty_print(to_print[key], indent+2)
            print indent * "    " + "}"
        elif isinstance(to_print, list):
            print indent * "    " + "["
            for value in to_print:
                self.pretty_print(value, indent + 1)
            print indent * "    " + "]"
        elif isinstance(to_print, tuple):
            print indent * "    " + "("
            for value in to_print:
                self.pretty_print(value, indent + 1)
            print indent * "    " + ")"
        else:
            print indent * "   " + str(to_print)

    def tearDown(self):
        pass

if __name__ == "__main__":
    testsuite = unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=1).run(testsuite)

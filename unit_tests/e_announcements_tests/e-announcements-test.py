import os
import tinker
import unittest
import tempfile


class EAnnouncementsTestCase(unittest.TestCase):

    # This method is designed to set up a temporary database, such that the tests won't affect the real database
    def setUp(self):
        self.db_fd, tinker.app.config['DATABASE'] = tempfile.mkstemp()
        self.app = tinker.app.test_client()

    # All these middle methods are individual tests. unittest will automatically run all of these methods and tell you
    # which tests, if any, failed. If they all pass, then it says "OK"
    def test_index(self):
        rv = self.app.get('/')
        assert b'<div class="large-12 columns">' in rv.data

    def test_new(self):
        rv = self.app.get('/new')
        assert b'<form id="eannouncementform" action="/e-announcement/" method="post" enctype="multipart/form-data">' \
               in rv.data

    def test_post(self):
        # This dict corresponds to the form <form><textarea id="input"> in templates/feedback.html;
        # the keys of the dict correspond to the ids of the input fields, and the values of the dict correspond to the
        # user's answers. This should throw a 500 because it doesn't have a mail client to send the email, but the
        # request is valid.
        rv = self.app.post('/submit-feedback', data=dict(
            e_announcement_id = "4"
        ), follow_redirects=True)
        print rv
        assert b' ' in rv.data

    'e_announcement_id'
    # Corresponding to the setUp method, this method unlinks the temporary database so that it can be released from RAM
    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(tinker.app.config['DATABASE'])

if __name__ == '__main__':
    unittest.main()

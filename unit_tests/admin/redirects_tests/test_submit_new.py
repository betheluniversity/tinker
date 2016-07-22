from redirects_base import RedirectsBaseTestCase


class SubmitNewTestCase(RedirectsBaseTestCase):
    #######################
    ### Utility methods ###
    #######################

    def create_new_form_submission(self, from_path, to_url, short, expiration):
        return {'new-redirect-from': from_path,
                'new-redirect-to': to_url,
                'short-url': short,
                'expiration-date': expiration
                }

    #######################
    ### Testing methods ###
    #######################

    def test_new_valid(self):
        form_contents = self.create_new_form_submission("from?", "to!", "on", "Fri Jul 01 2016")
        response = super(SubmitNewTestCase, self).send_post('/admin/redirect/new-submit', form_contents)
        assert b'<Redirect /from? to to!>' in response.data
        # add an assertion that it got added to the database

    def test_new_invalid_from(self):
        form_contents = self.create_new_form_submission(None, "to!", "on", "Fri Jul 01 2016")
        response = super(SubmitNewTestCase, self).send_post('/admin/redirect/new-submit', form_contents)
        assert b'<Redirect /from? to to!>' not in response.data

    def test_new_invalid_to(self):
        form_contents = self.create_new_form_submission("from?", None, "on", "Fri Jul 01 2016")
        response = super(SubmitNewTestCase, self).send_post('/admin/redirect/new-submit', form_contents)
        assert b'<Redirect /from? to to!>' not in response.data

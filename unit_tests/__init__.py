# In an ideal world, here are some features that I would like to implement to unit testing:
# 1. Integrate the unit tests into the Travis checker plugin for github, so that all changes will automatically get
#       tested by the unit tests
# 2. Make the unit tests much more robust; instead of just testing endpoints of a module, it can also check that each
#       respective DB or Cascade object gets updated appropriately so that there's no possibility of silent failures
# 3. A web interface that could be integrated into our future dashboard, such that they can select which module (or all)
#       they want to test, click a button online, and the tests all get run and the results displayed in a browser
# 4. Find some way to pass test object ids back and forth between unit tests so that the test_sequentially files can be
#       split into individual, granular unit tests.
# 5. Write a unit test factory class that can auto-generate unit test files given a set of parameters about the endpoint
#       it's going to be testing.
#
# Currently, the unit testing suite takes about 3 minutes to run.

if __name__ == "__main__":
    import unittest
    testsuite = unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=1).run(testsuite)

# Delete these E-Announcements:
# 9ffa06128c5865133973dd3e290626cc
# 9fc4ea4e8c5865133973dd3e401add56
# 9fb731728c5865133973dd3ef6340726

# Missing unit test files:
# admin/redirects/new_api_submit
# admin/redirects/new_api_submit_asset_expiration
# admin/redirects/new_internal_redirect_submit
# e_announcements/edit_all
# events/confirm
# events/edit_all
# events/reset_tinker_edits
# faculty_bio/confirm
# faculty_bio/delete_confirm
# faculty_bio/activate
# faculty_bio/edit_all
# office_hours/rotate_hours

# TODO:
# Improve test_sequentially failure message specificity so that it tells you which endpoint failed
# Add more context to failure messages, like what was returned, so that they can see why it failed

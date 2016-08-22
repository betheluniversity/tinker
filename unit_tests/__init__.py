# In an ideal world, here are some features that I would like to implement to unit testing:
# 1. Make the unit tests much more robust; instead of just testing endpoints of a module, it can also check that each
#       respective DB or Cascade object gets updated appropriately so that there's no possibility of silent failures
# 2. A web interface that could be integrated into our future dashboard, such that they can select which module (or all)
#       they want to test, click a button online, and the tests all get run and the results displayed in a browser
# 3. Find some way to pass test object ids back and forth between unit tests so that the test_sequentially files can be
#       split into individual, granular unit tests.
# 4. Write a unit test factory class that can auto-generate unit test files given a set of parameters about the endpoint
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

# In an ideal world, here are some features that I would like to implement to unit testing:
# 1. Custom error messages for each test; that way anyone could run this file and understand each failure or error in
#       the console, without having to figure it out first.
# 2. A web interface that could be integrated into our future dashboard, such that they can select which module (or all)
#       they want to test, click a button online, and the tests all get run and the results displayed in a browser

if __name__ == "__main__":
    import unittest
    testsuite = unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=1).run(testsuite)

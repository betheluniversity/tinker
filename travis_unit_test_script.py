import sys
import unittest

testsuite = unittest.TestLoader().discover('unit_tests')
runner = unittest.TextTestRunner(verbosity=1).run(testsuite)
sys.exit(len(runner.failures))

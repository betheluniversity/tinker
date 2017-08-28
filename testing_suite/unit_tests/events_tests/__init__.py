import unittest

# from multiprocessing.dummy import Pool as ThreadPool
from testing_suite.utilities import get_tests_in_this_dir

if __name__ == "__main__":
    testsuite = get_tests_in_this_dir(".")
    unittest.TextTestRunner(verbosity=1).run(testsuite)

    # def thread_func(arg):
    #     testsuite = get_tests_in_this_dir(".")
    #     results = unittest.TextTestRunner(stream=None).run(testsuite)
    #
    #     if len(results.errors) > 0:
    #         for err in results.errors:
    #             error_message = err[1]
    #             print error_message
    #
    #     print 'Thread #%s finished' % arg
    #
    # pool = ThreadPool(100)
    # results = pool.map(thread_func, range(100))

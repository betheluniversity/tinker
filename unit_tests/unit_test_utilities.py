import os
from inspect import stack

from discover import DiscoveringTestLoader


def get_tests_in_this_dir(path):
    # return unittest.TestLoader().discover(path)
    if path == ".":
        current_frame = stack()[1]
        file_of_current_frame = current_frame[0].f_globals.get('__file__', None)
        path = os.path.dirname(file_of_current_frame)
    test_loader = DiscoveringTestLoader()
    return test_loader.discover(path, pattern="test_*.py")

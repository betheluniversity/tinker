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


def pretty_print(obj, depth=0, console=True):
    if console:
        tab = ' ' * 4
        newline = '\n'
    else:
        tab = '&nbsp;' * 4
        newline = '<br/>'
    indent = tab * depth
    to_return = ''
    if isinstance(obj, list):
        to_return += '[' + newline + indent
        for item in obj:
            to_return += tab + pretty_print(item, depth=depth + 1, console=console) + ',' + newline + indent
        to_return += ']'
    elif isinstance(obj, tuple):
        to_return += '(' + newline + indent
        for item in obj:
            to_return += tab + pretty_print(item, depth=depth + 1, console=console) + ',' + newline + indent
        to_return += ')'
    elif isinstance(obj, dict):
        to_return += '{' + newline + indent
        for key in obj.keys():
            to_return += tab + "'%s': " % key + pretty_print(obj[key], depth=depth + 1, console=console) \
                         + ',' + newline + indent
        to_return += '}'
    elif isinstance(obj, (str, unicode)):
        to_return += "'%s'" % obj
    elif isinstance(obj, (int, long, float)):
        to_return += str(obj)
    else:
        # This should be equivalent to str(obj) for most cases, but this is more robust in case anyone wrote a custom
        # __repr__() function for the object being pretty printed.
        try:
            to_return += obj.__repr__()
        except:
            to_return += str(obj)
    return to_return


# I wrote this method because I found myself trying to figure out what type of object was being used and from where it
# was being imported far more often than I would like. Rather than try to remember all the different lines, instead I
# wrote this method that I can import and use anywhere.
def describe(object_to_describe):
    # Convert vars() from dictproxy to dict
    vars_alias = vars(object_to_describe)
    vars_dict_copy = {}
    for key in vars_alias.keys():
        vars_dict_copy[key] = vars_alias[key]
    to_return = {
        'represtation': repr(object_to_describe),
        'class': object_to_describe.__class__.__name__,
        'variables': vars_dict_copy,
        'methods': dir(object_to_describe)
    }
    return pretty_print(to_return)

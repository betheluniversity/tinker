import sys
import unittest
# import sqlite3
# from tinker import app
# from StringIO import StringIO
from unit_tests.unit_test_utilities import get_tests_in_this_dir


# def create_temp_db():
#     # Read database to tempfile
#     db_path = app.config['SQLALCHEMY_DATABASE_URI'].split('sqlite:///')[1].split('app.db')[0] + "testing_db.db"
#     con = sqlite3.connect(db_path)
#     tempfile = StringIO()
#     for line in con.iterdump():
#         tempfile.write('%s\n' % line)
#     con.close()
#     tempfile.seek(0)
#
#     # Create a database in memory and import from tempfile
#     mem_db = sqlite3.connect(":memory:")
#     mem_db.cursor().executescript(tempfile.read())
#     mem_db.commit()
#     mem_db.row_factory = sqlite3.Row
#     return mem_db


testsuite = get_tests_in_this_dir('unit_tests')
runner = unittest.TextTestRunner(verbosity=1).run(testsuite)
sys.exit(len(runner.failures) + len(runner.errors))

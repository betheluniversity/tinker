import os
import shutil
import tempfile
import tinker
from unit_tests import BaseTestCase


class RedirectsBaseTestCase(BaseTestCase):

    def show_permissions(self, filepath):
        # Adapted from https://hg.python.org/cpython/file/3.5/Lib/stat.py
        mode = os.stat(filepath).st_mode
        perm = []

        S_IFDIR = 0o040000  # directory
        S_IFCHR = 0o020000  # character device
        S_IFBLK = 0o060000  # block device
        S_IFREG = 0o100000  # regular file
        S_IFIFO = 0o010000  # fifo (named pipe)
        S_IFLNK = 0o120000  # symbolic link
        S_ISUID = 0o4000  # set UID bit
        S_ISGID = 0o2000  # set GID bit
        S_ISVTX = 0o1000  # sticky bit
        S_IRUSR = 0o0400  # read by owner
        S_IWUSR = 0o0200  # write by owner
        S_IXUSR = 0o0100  # execute by owner
        S_IRGRP = 0o0040  # read by group
        S_IWGRP = 0o0020  # write by group
        S_IXGRP = 0o0010  # execute by group
        S_IROTH = 0o0004  # read by others
        S_IWOTH = 0o0002  # write by others
        S_IXOTH = 0o0001  # execute by others
        _filemode_table = (
            ((S_IFLNK, "l"),
             (S_IFREG, "-"),
             (S_IFBLK, "b"),
             (S_IFDIR, "d"),
             (S_IFCHR, "c"),
             (S_IFIFO, "p")),
            ((S_IRUSR, "r"),),
            ((S_IWUSR, "w"),),
            ((S_IXUSR | S_ISUID, "s"),
             (S_ISUID, "S"),
             (S_IXUSR, "x")),
            ((S_IRGRP, "r"),),
            ((S_IWGRP, "w"),),
            ((S_IXGRP | S_ISGID, "s"),
             (S_ISGID, "S"),
             (S_IXGRP, "x")),
            ((S_IROTH, "r"),),
            ((S_IWOTH, "w"),),
            ((S_IXOTH | S_ISVTX, "t"),
             (S_ISVTX, "T"),
             (S_IXOTH, "x"))
        )

        for table in _filemode_table:
            for bit, char in table:
                if mode & bit == bit:
                    perm.append(char)
                    break
            else:
                perm.append("-")

        print "".join(perm)

    # This method is designed to set up a temporary database, such that the tests won't affect the real database
    def setUp(self):
        self.temp_dir = tempfile.gettempdir()
        self.temp_path = os.path.join(self.temp_dir, 'tempDB.db')
        self.permanent_path = tinker.app.config['SQLALCHEMY_DATABASE_URI']
        shutil.copy2(tinker.app.config['SQLALCHEMY_DATABASE_URI'].split('sqlite://')[1], self.temp_path)
        os.system("chown www-data %s" % self.temp_path)
        tinker.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.temp_path
        tinker.app.testing = True
        tinker.app.config['WTF_CSRF_ENABLED'] = False
        tinker.app.config['WTF_CSRF_METHODS'] = []
        self.app = tinker.app.test_client()

    # Corresponding to the setUp method, this method deletes the temporary database
    def tearDown(self):
        tinker.app.config['SQLALCHEMY_DATABASE_URI'] = self.permanent_path
        os.remove(self.temp_path)
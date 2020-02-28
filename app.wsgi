import sys
import os

path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, path)

#log to stderr instead of stdout
activate_this = '/opt/tinker/env/bin/activate_this.py'
exec(compile(open(activate_this).read(), activate_this, 'exec'), dict(__file__=activate_this))

import logging
logging.basicConfig(stream=sys.stderr)

from tinker import app as application
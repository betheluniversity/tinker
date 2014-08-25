#!/opt/tinker/env/bin/python

from tinker.redirects.models import BethelRedirect
from tinker import db
import fileinput
import os
import sys
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

while True:
	request = sys.stdin.readline().strip()
	print request
	if request == '/about':
		print sys.stdout.write('http://tinker.bethel.edu/redirect/about-redirect\n')
	else:
		sys.stdout.write('__NULL__\n')
	sys.stdout.flush()



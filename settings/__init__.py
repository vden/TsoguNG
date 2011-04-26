# -*- coding: utf-8 -*-

from general import *
from cache import *
from amqp import *

try:
	from local import *
except:
	print "Create settings/local.py"

import sys
import logging

if not hasattr(logging, 'tsogung_config'):
	import log
	logging.root.setLevel(DEBUG and logging.DEBUG or logging.INFO)

from django.core.files.storage import FileSystemStorage
photo_fs = FileSystemStorage(location=PHOTOS_ROOT, base_url=PHOTOS_URL)
file_fs = FileSystemStorage(location=FILE_ROOT, base_url=FILE_URL)

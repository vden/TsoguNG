# -*- coding: utf-8 -*-

import os, re
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

def render_to(template_path):
	def decorator(func):
		def wrapper(request, *args, **kw):
			output = func(request, *args, **kw)
			if not isinstance(output, dict):
				return output
			return render_to_response(template_path, output,
				context_instance=RequestContext(request))
		return wrapper
	return decorator

## http://www.djangosnippets.org/snippets/873/
import sys

from django.conf import settings as django_settings

class SettingsProcessor(object):
	def __getattr__(self, attr):
		if attr == '__file__':
			# autoreload support in dev server
			return __file__
		else:
			return lambda request: {attr: getattr(django_settings, attr)}

sys.modules[__name__ + '.settings'] = SettingsProcessor()

import Image, os
def handle_thumb(storage, image_obj, thumb_obj, width, height):
	image_name = image_obj.name
	thumb_name = thumb_obj.name
	# create thumbnail
	thumb = image_obj.name + ('-t%sx%s.jpg' % (width, height))
	try:
		t = Image.open(storage.location + '/' + image_obj.name)

		if t.mode not in ('L', 'RGB'):
			t = t.convert('RGB')

		t.thumbnail((width, height), Image.ANTIALIAS)

#			w, h = t.size
#			if float(w)/h < float(width)/height:
#				t = t.resize((width, h*width/w), Image.ANTIALIAS)
#			else:
#				t = t.resize((w*height/h, height), Image.ANTIALIAS)
#			w, h = t.size
#			t = t.crop( ((w-width)/2, (h-height)/4, (w-width)/2+width, (h-height)/4+height) )

		t.save(storage.location + '/' + thumb, 'JPEG')
		os.chmod(storage.location + '/' + thumb, 0666)
		thumb_obj = thumb
	except Exception, E:
		print E
	if image_name==thumb_name:
		os.remove(storage.location + '/' + image_name)
	return thumb_obj

def thumbnail_cropped(storage, image_obj, size, drop_cache=False):
	width, height = size
	if os.path.exists(storage.location + '/' + image_obj.name + '-t%sx%s.jpg'%size) and not drop_cache:
		img = Image.open(storage.location + '/' + image_obj.name + '-t%sx%s.jpg'%size)
	else:
		img = Image.open(storage.location + '/' + image_obj.name)

		if img.mode not in ('L', 'RGB'):
			img = img.convert('RGB')

		w, h = img.size

		if float(w)/h < float(width)/height:
			img = img.resize((width, h*width/w), Image.ANTIALIAS)
		else:
			img = img.resize((w*height/h, height), Image.ANTIALIAS)

		w, h = img.size
		print ((w-width)/2, (h-height)/4, (w-width)/2+width, (h-height)/4+height)
		img = img.crop( ((w-width)/2, (h-height)/4, (w-width)/2+width, (h-height)/4+height) )
		img.save(storage.location + '/' + image_obj.name + '-t%sx%s.jpg'%size, 'JPEG')
		os.chmod(storage.location + '/' + image_obj.name + '-t%sx%s.jpg'%size, 0666)
	return img

def thumbnail_resized(storage, image_obj, size, drop_cache=False):
	width, height = size
	if os.path.exists(storage.location + '/' + image_obj.name + '-tr%sx%s.jpg'%size) and not drop_cache:
		img = Image.open(storage.location + '/' + image_obj.name + '-tr%sx%s.jpg'%size)

	else:
		img = Image.open(storage.location + '/' + image_obj.name)

		if img.mode not in ('L', 'RGB'):
			img = img.convert('RGB')

		w, h = img.size

		if float(w)/h > float(width)/height:
			img = img.resize((width, h*width/w), Image.ANTIALIAS)
		else:
			img = img.resize((w*height/h, height), Image.ANTIALIAS)

		w, h = img.size
		img.save(storage.location + '/' + image_obj.name + '-tr%sx%s.jpg'%size, 'JPEG')
		os.chmod(storage.location + '/' + image_obj.name + '-tr%sx%s.jpg'%size, 0666)
	return img

def URLify(s, num_chars=None, strong=True):
	'''
	Changes, e.g., "Petty theft" to "petty_theft".
	This function is the Python equivalent of the javascript function
	of the same name in django/contrib/admin/media/js/urlify.js.
	It can get invoked for any field that has a prepopulate_from
	attribute defined, although it only really makes sense for
	SlugFields.
	
	NOTE: this implementation corresponds to the Python implementation
		  of the same algorithm in django/contrib/admin/media/js/urlify.js
	'''
	# remove all these words from the string before urlifying
#	removelist = ["a", "an", "as", "at", "before", "but", "by", "for",
#		      "from", "is", "in", "into", "like", "of", "off", "on",
#		      "onto", "per", "since", "than", "the", "this", "that",
#		      "to", "up", "via", "with"]
#	ignore_words = '|'.join([r for r in removelist])
#	ignore_words_pat = re.compile(r'\b(%s)\b' % ignore_words, re.I)
	if strong:
		ignore_chars_pat = re.compile(r'[^-a-z0-9\s]')
	else:
		ignore_chars_pat = re.compile(r'[^-a-z0-9\s\/\.\_]')
	inside_space_pat = re.compile(r'[-\s]+')

	RUSSIAN_MAP =	{
		u"а": "a",    u"к": "k",    u"х": "kh",
		u"б": "b",    u"л": "l",    u"ц": "ts",
		u"в": "v",    u"м": "m",    u"ч": "ch",
		u"г": "g",    u"н": "n",    u"ш": "sh",
		u"д": "d",    u"о": "o",    u"щ": "shch",
		u"е": "e",    u"п": "p",    u"ъ": "",
		u"ё": "e",    u"р": "r",    u"ы": "y",
		u"ж": "zh",   u"с": "s",    u"ь": "",
		u"з": "z",    u"т": "t",    u"э": "e",
		u"и": "i",    u"у": "u",    u"ю": "ju",
		u"й": "j",    u"ф": "f",    u"я": "ja"
	} 
	
	s = s.lower()					# convert to lowercase
	result = ""
	for c in s:
		try:
			result += (c in RUSSIAN_MAP.keys() and RUSSIAN_MAP[c] or c)
		except:
			pass
	#s = ignore_words_pat.sub('', s)  # remove unimportant words

	s = result
	s = ignore_chars_pat.sub('', s)  # remove unneeded chars
	s = s.strip()					# trim leading/trailing spaces
	s = inside_space_pat.sub('-', s) # convert remaining spaces to hyphens
	if num_chars is not None:
		s = s[:num_chars]			# trim to first num_chars chars

	return s

import re
from datetime import datetime
def parseDateTime(s):
	"""Create datetime object representing date/time
	   expressed in a string
 
	Takes a string in the format produced by calling str()
	on a python datetime object and returns a datetime
	instance that would produce that string.
 
	Acceptable formats are: "YYYY-MM-DD HH:MM:SS.ssssss+HH:MM",
							"YYYY-MM-DD HH:MM:SS.ssssss",
							"YYYY-MM-DD HH:MM:SS+HH:MM",
							"YYYY-MM-DD HH:MM:SS"
	Where ssssss represents fractional seconds.	 The timezone
	is optional and may be either positive or negative
	hours/minutes east of UTC.
	"""
	if s is None:
		return None
	# Split string in the form 2007-06-18 19:39:25.3300-07:00
	# into its constituent date/time, microseconds, and
	# timezone fields where microseconds and timezone are
	# optional.
	m = re.match(r'(.*?)(?:\.(\d+))?(([-+]\d{1,2}):(\d{2}))?$',
				 str(s))
	datestr, fractional, tzname, tzhour, tzmin = m.groups()
 
	# Create tzinfo object representing the timezone
	# expressed in the input string.  The names we give
	# for the timezones are lame: they are just the offset
	# from UTC (as it appeared in the input string).  We
	# handle UTC specially since it is a very common case
	# and we know its name.
	if tzname is None:
		tz = None
	else:
		tzhour, tzmin = int(tzhour), int(tzmin)
		if tzhour == tzmin == 0:
			tzname = 'UTC'
		tz = FixedOffset(timedelta(hours=tzhour,
								   minutes=tzmin), tzname)
 
	# Convert the date/time field into a python datetime
	# object.
	x = datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")
 
	# Convert the fractional second portion into a count
	# of microseconds.
	if fractional is None:
		fractional = '0'
	fracpower = 6 - len(fractional)
	fractional = float(fractional) * (10 ** fracpower)
 
	# Return updated datetime object with microseconds and
	# timezone information.
	return x.replace(microsecond=int(fractional), tzinfo=tz)


import urllib2, base64
def http_auth_request(url, username, password):
	req = urllib2.Request(url)

	base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
	authheader =  "Basic %s" % base64string
	req.add_header("Authorization", authheader)

	handle = urllib2.urlopen(req)

	return handle

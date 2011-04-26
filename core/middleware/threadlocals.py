# -*- coding: utf-8 -*-

# threadlocals middleware
from utils.messages import PortalMessageSlot
try:
	from threading import local
except ImportError:
	from django.utils._threading_local import local

_thread_locals = local()

def get_current_user():
	return getattr(_thread_locals, 'user', None)

def get_request():
	return getattr(_thread_locals, 'request', None)

def set_portal_message(mes):
	try:
		_thread_locals.messages.append(mes)
	except:
		pass

def get_portal_message():
	try:
		return _thread_locals.messages
	except Exception, E:
		return None

def get_thread_locals(varname):
	return getattr(_thread_locals, varname, None)

def set_thread_locals(varname, value):
	return setattr(_thread_locals, varname, value)

def set_cookie(key, value, max_age=None, expires=None, path='/', domain=None, secure=None):
	_thread_locals.cookies[key] = {'value': value, 'max_age': max_age, 'expires': expires, 'path': path,
				       'domain': domain, 'secure': secure}

class ThreadLocals(object):
	"""Middleware that gets various objects from the
	request object and saves them in thread local storage."""
	def process_request(self, request):
		_thread_locals.user = getattr(request, 'user', None)
		_thread_locals.request = request
		_thread_locals.messages = PortalMessageSlot()
		_thread_locals.cookies = {}
		# pm = getattr(request.GET, 'portal_message', None)
		pm = request.GET.get('portal_message', None)
		if pm:
			from utils.portal_messages import portal_messages
			for mid in pm.split(','):
				try:
					set_portal_message(portal_messages[mid])
				except:
					pass

	def process_response(self, request, response):
		if not getattr(_thread_locals, 'cookies', None): return response
		for cookie in _thread_locals.cookies.keys():
			print "PROCESS COOKIE", cookie
			c = _thread_locals.cookies[cookie]
			response.set_cookie(cookie, c['value'], c['max_age'], c['expires'], c['path'], 
					    c['domain'], c['secure'])
		return response



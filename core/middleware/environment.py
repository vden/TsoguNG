# -*- coding: utf-8 -*-

"""
	Модуль окружения.

	@author: Vlasov Dmitry
	@contact: scailer@tsogu.ru
	@organization: TSOGU
	@status: функционирует
	@version: 1.0
"""
try:
	from threading import local
except ImportError:
	from django.utils._threading_local import local
from utils.messages import PortalMessageSlot, PortalMessage

_thread_locals = local()

def set_cookie(key, value, max_age=None, expires=None, path='/', domain=None, secure=None):
	_thread_locals.cookies[key] = {'value': value, 'max_age': max_age, 'expires': expires, 'path': path,
				       'domain': domain, 'secure': secure}

class ThreadLocals(object):
	"""
		Мидлварь для создания окружения
	"""

	def __init__(self):
		"""
			Метод вызывается при старте сервера.
		"""
		from core import REGISTRUM
		self.REGISTRUM = REGISTRUM

	def process_request(self, request):
		"""
			Метод вызывается перед парсингом параметров запроса.
		"""
		request.classes = [dict(val.items()+[('name',key)]) for key,val in self.REGISTRUM['types'].items()
					if not key in ['News','Event','Dissertation','Poll'] and val['user']]
		request.portal_message = PortalMessageSlot()

		pm = request.GET.get('portal_message', None)
		if pm:
			from utils.portal_messages import portal_messages
			for mid in pm.split(','):
				try:
					set_portal_message(portal_messages[mid])
				except:
					pass

	def process_view(self, request, view_func, view_args, view_kwargs):
		"""
			Метод вызывается перед исполнением view.
		"""
		from core.views import get_object_by_url
		from core.models import Alias
		from django.http import HttpResponseRedirect
		if view_func.__name__ is 'dispatcher':
			path = [x for x in view_kwargs['path_info'].split("/") if x]
			if path:
				res = Alias.objects.filter(url=path[0])
				if res:
					view_kwargs['path_info'] = '%s%s' % (res[0].bid.get_absolute_url(),'/'.join(path[1:]))
					view_kwargs['redirect'] = True
			request.main_object = get_object_by_url(view_kwargs['path_info'])
			request.action = view_kwargs['action']

	def process_response(self, request, response):
		"""
			Метод вызывается после исполнениея кода во view.
		"""
		if not getattr(_thread_locals, 'cookies', None): return response
		for cookie in _thread_locals.cookies.keys():
			c = _thread_locals.cookies[cookie]
			response.set_cookie(cookie, c['value'], c['max_age'], c['expires'], c['path'],
					    c['domain'], c['secure'])
		return response

	def process_exception(self, request, exception):
		"""
			Метод вызывается при возникновении исключения.
		"""
		from core.portal.exceptions import Http403, Http302, Http404
		from django.http import HttpResponseRedirect
		from django.conf import settings
		from core.portal.render import render_error

		if isinstance(exception, Http302):
			return HttpResponseRedirect(exception.url)

		if isinstance(exception, Http403) and not settings.DEBUG:
			return render_error(request, exception)

		if isinstance(exception, Http404) and not settings.DEBUG:
			return render_error(request, exception)

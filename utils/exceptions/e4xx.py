# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect 
from django.template import Context, RequestContext, loader as template_loader

class Http400(Exception):
	""" Bad Request. The request could not be understood by the server due to malformed syntax """
	def render(self, request):
		return HttpResponse(u'Ошибка 400')

class Http401(Exception):
	""" Unauthorized. The request requires user authentication """
	def render(self, request):
		return HttpResponse(u'Ошибка 400')

class Http402(Exception):
	""" Payment Required. This code is reserved for future use """
	def render(self, request):
		return HttpResponse(u'Ошибка 400')

class Http403(Exception):
	""" Forbidden. The server understood the request, but is refusing to fulfill it """
	def render(self, request):
		print 'UUU',request.user.is_anonymous()
		if not request.user.is_anonymous():
			return template_loader.get_template('exceptions/403.html').render(RequestContext(request,{}))
		else:
			raise self

	def response(self, request):
		return HttpResponseRedirect('/action/login/')


class Http404(Exception):
	""" Forbidden. The server understood the request, but is refusing to fulfill it """
	def render(self, request):
		return HttpResponse(u'Ошибка 400')

class Http405(Exception):
	""" Method Not Allowed. The method specified in the Request-Line is not allowed for the resource identified by the Request-URI """
	def render(self, request):
		return HttpResponse(u'Ошибка 400')

class Http408(Exception):
	""" Request Timeout. The client did not produce a request within the time that the server was prepared to wait """
	def render(self, request):
		return HttpResponse(u'Ошибка 400')

class Http409(Exception):
	""" Conflict. The request could not be completed due to a conflict with the current state of the resource """
	def render(self, request):
		return HttpResponse(u'Ошибка 400')

class Http410(Exception):
	""" Gone. The requested resource is no longer available at the server and no forwarding address is known """
	def render(self, request):
		return HttpResponse(u'Ошибка 400')


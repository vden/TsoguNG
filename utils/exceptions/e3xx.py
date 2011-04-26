# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseRedirect 

class Http301(Exception):
	""" Moved Permanently. The requested resource has been assigned a new permanent URI and any future references to this resource SHOULD use one of the returned URIs"""
	def render(self, request):
		return HttpResponse(u'Перенаправление 301')

class Http302(Exception):
	""" Found. The requested resource resides temporarily under a different URI """
	def response(self, request):
		return HttpResponseRedirect(self.args and self.args[0] or '/')

class Http307(Exception):
	""" Temporary Redirect. The requested resource resides temporarily under a different URI """
	def render(self, request):
		return HttpResponse(u'Перенаправление 307')

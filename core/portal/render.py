# -*- coding: utf-8 -*-

"""
	Декораторы рендеринга.

	@author: Vlasov Dmitry
	@contact: scailer@tsogu.ru
	@organization: TSOGU
	@status: функционирует
	@version: 1.0
"""

from django.template import Context, RequestContext, loader as template_loader
from django.http import HttpResponse
from functools import wraps

def render_to_portal(*args, **kw):
	"""
		Отрисовка результата вызова функции в обрамлении портала.

		@return: HttpResponse/html

		@param obj: Portal Object
		@type obj: BaseObject

		@param request: Request
		@type request: Request
	"""
	def func(fn):
		@wraps(fn)
		def call(*cargs, **ckw):
			from core.portal.utils import form_page, get_object_by_url
			request = ckw.get('request') or cargs[0]
			obj = getattr(request, 'main_object', get_object_by_url('/'))
			if 'template' in kw:
				data = template_loader.get_template(kw['template']).render(
							RequestContext(request, fn(*cargs, **ckw)))
			else:
				data = fn(*cargs, **ckw)
			columns = kw.get('columns', ('a', 'b', 'c'))
			return form_page(request, obj.get_absolute_url(), obj, edit=False, new_type=None, data=data, columns=columns)
		return call
	return func

def render_ajax(type='text', template=None):
	"""
		Свободный типизированный вывод результата вызова функции.
		@return: HttpResponse/<html/text/json>

		@param type: html/text/json
		@type type: string
	"""
	def func(fn):
		@wraps(fn)
		def call(*cargs, **ckw):
			from django.utils import simplejson
			from django.template import Context, RequestContext, loader as template_loader
			request = ckw.get('request') or cargs[0]
			data = fn(*cargs, **ckw)
			if type == 'text':
				return HttpResponse(unicode(data))
			elif type == 'json':
				return HttpResponse(simplejson.dumps(data), mimetype='application/json')
			elif type == 'html':
				return HttpResponse(template and template_loader.get_template(template).render(RequestContext(request, data)) or data)
			else:
				raise Exception(u'Render_ajax decorator: Unknown data type %s' % type)
		return call
	return func

def render_as_redirect(*args, **kw):
	"""
		Перенаправление вызова.
		@return: HttpResponseRedirect
	"""
	def func(fn):
		def call(*cargs, **ckw):
			from django.http import HttpResponseRedirect
			url = fn(*cargs, **ckw)
			return HttpResponseRedirect(url)
		call.func_name = fn.func_name
		return call
	return func

def render_rss(*args, **kw):
	"""
		Рендеринг RSS ленты
	"""
	def func(fn):
		def call(*cargs, **ckw):
			from django.contrib.syndication.views import feed
			request = cargs[1]
			data = fn(*cargs, **ckw)
			return feed(request, **data)
		call.func_name = fn.func_name
		return call
	return func

def render_error(request, error):
	return HttpResponse(template_loader.get_template('error.html').render(RequestContext(request, {'error': error})), status=error.code)

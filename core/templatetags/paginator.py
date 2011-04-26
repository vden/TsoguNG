# -*- coding: utf-8 -*-

"""
	Универсальный педженатор на основе GET-запросов

	@author: Vlasov Dmitry
	@contact: scailer@tsogu.ru
	@organization: TSOGU
	@status: функционирует
"""

import re
from django import template
from django.core.paginator import Paginator
from django.template import Context, RequestContext, loader as template_loader
register = template.Library()

@register.tag
def paginator(parser, token):
	""" {% paginator array 10 as pages %} """
	try:
		param_array = token.split_contents()
		data = param_array[1]
		limit = param_array[2]
		var = param_array[-1]
	except Exception:
		raise template.TemplateSyntaxError

	return PaginatorNode(data, limit, var)


class PaginatorView(Paginator):
	current_page = 1
	extra_query=''
	is_begining = True
	is_ending = True
	slice_params = [0,0]

	def set_current_page(self, page, max_range=2):
		self.current_page = page

		# Делаем многоточие, если страниц слишком много
		pages = super(PaginatorView, self).page_range
		if len(pages) > 2*max_range+1:
			self.slice_params[0] = int(page-max_range-1>0 and page-max_range-1 or 0)
			self.is_begining = self.slice_params[0] < 1
			self.slice_params[1] = int(page+max_range)
			self.is_ending = self.slice_params[1] >= len(pages)

	@property
	def get_current_page(self):
		return self.page(self.current_page)

	def render_pages(self, tpl="paginator/pages.html"):
		context = {'page':self.get_current_page, 'pages':self, 'query':self.extra_query}
		return template_loader.get_template(tpl).render(Context(context))

	def _get_page_range(self):
		pages = super(PaginatorView, self).page_range
		if not self.is_begining or not self.is_ending:
			pages = pages[self.slice_params[0]:self.slice_params[1]]
		return pages
	page_range = property(_get_page_range)


class PaginatorNode(template.Node):
	def __init__(self, data, limit, var):
		self.data = template.Variable(data)
		self.limit = template.Variable(limit)
		self.var = var

	def render(self, context):
		self.data = self.data.resolve(context)
		self.limit = int(self.limit.resolve(context))
		paginator = PaginatorView(self.data, self.limit)

		# Трансляция запроса
		qs = context['request'].META['QUERY_STRING']
		sub_qs = re.search(r'&?page=\d+',qs)
		if sub_qs:
			sub_qs = sub_qs.group()
			qs = qs.replace(sub_qs,'')
		paginator.extra_query = qs 

		try:
			paginator.set_current_page(int(context['request'].GET['page']), max_range=3)
		except:
			pass

		context[self.var] = paginator
		return u''

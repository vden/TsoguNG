# -*- coding: utf-8 -*-
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def strlimit(value, limit=50):
	""" Обрезает строку до нужной длинны и ставит многоточие, для обрезанных строк """
	try:
		return len(value)>limit and '%s...' % value[:limit] or value
	except:
		return value

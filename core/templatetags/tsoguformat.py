# -*- coding: utf-8 -*-
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
def money(value):
	"""  Приводит число к виду x'xxx'xxx """
	try:
		if not value:
			return value

		vsum = str(value)
		return u' '.join([x for x in (vsum[:-9],vsum[-9:-6],vsum[-6:-3],vsum[-3:]) if x]) 
	except:
		return value

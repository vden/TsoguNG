# -*- coding: utf-8 -*-

from django import template
from pytils import dt
register = template.Library()

@register.inclusion_tag('complain.html', takes_context=True)
def complain(context):
	request = context['request']
	return {'object': request.main_object, 'url': request.path}

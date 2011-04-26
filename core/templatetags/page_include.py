# -*- coding: utf-8 -*-

from django import template
from core.views import get_object_by_url

register = template.Library()

@register.inclusion_tag('page_include.html')
def page_include(page_url, parent_obj=None):
    if parent_obj:
        page_url = "%s%s"%(parent_obj.get_absolute_url(), page_url)
    try:
        obj = get_object_by_url(page_url)
    except:
        obj = None

    return {"obj": obj}

    

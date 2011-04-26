# -*- coding: utf-8 -*-

from django import template

register = template.Library()

@register.simple_tag
def col_eval(lst):
    try:
        l = len(lst)
        w = 100./float(l)
    except:
        w = 100.
        l = 1

    col = "<col width='%s%%'>"%w
    return col*l

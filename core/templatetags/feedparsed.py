# -*- coding: utf-8 -*-
# http://www.djangosnippets.org/snippets/1595/

from django.template import Library
import datetime 

register = Library()

def feedparsed(value):
    return datetime.datetime(*value[:7]) + datetime.timedelta(hours=6)

register.filter(feedparsed)

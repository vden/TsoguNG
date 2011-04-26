# -*- coding:utf-8 -*-

from django import template

from utils.snippets import parseDateTime
from pytils.dt import ru_strftime
from datetime import datetime

register = template.Library()

@register.simple_tag
def date_between(start_date, end_date, show_prep=True, always_show_year=False, fmt1=u"%d %B", fmt2=u"%d %B %Y г."):
    """
    Допустимые форматы: 
    "YYYY-MM-DD HH:MM:SS.ssssss+HH:MM",
    "YYYY-MM-DD HH:MM:SS.ssssss",
    "YYYY-MM-DD HH:MM:SS+HH:MM",
    "YYYY-MM-DD HH:MM:SS"
    """

    try:
        if not isinstance(start_date, datetime):
            start_date = parseDateTime(start_date)

        if start_date.day == 2: prep = u'со'
        else: prep = u'с'  
    
        if (end_date is None) or (end_date == start_date):
            if not show_prep: prep = u''
            return u"%s %s"%(prep, 
                           ru_strftime(fmt2, start_date, inflected=True))

        if not isinstance(end_date, datetime):
            end_date = parseDateTime(end_date)

        if start_date.year == end_date.year:
            fmt = fmt1
        else:
            fmt = fmt2
        
        if always_show_year:
            end_fmt = fmt2
        else:
            end_fmt = fmt

        return u"%s %s по %s"%(prep, 
                           ru_strftime(fmt, start_date, inflected=True), 
                           ru_strftime(end_fmt, end_date, inflected=True))
    except Exception, E:
        return unicode(E)

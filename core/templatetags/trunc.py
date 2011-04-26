# -*- coding: utf-8 -*-

from django import template
register = template.Library()

@register.filter
def trunc( string, number, dots='...'):
    """ 
    truncate the {string} to {number} characters
    print {dots} on the end if truncated
    
    usage: {{ "some text to be truncated"|trunc:6 }}
    results: some te...
    """
#    if not isinstance(string, str): string = unicode(string)
    if len(string) <= number:
        return string
    return string[0:number]+dots

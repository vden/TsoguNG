# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.inclusion_tag('show_config.html')
def show_config(obj):
    """
    пусть уже параметры с подчеркиванием на конце
    (потому что в начале нельзя, будет считаться скрытым полем)
    будут типа служебными, т.е. на страницах отображаться
    не будут, где показывается информация из конфигурации
    """
    cfg = {}
    for k,v in obj.config().items():
        if k[-1:]!='_' and v.strip()!='' and k not in ['last_editor','editing_history']:
            cfg[k] = v

    return {'config': cfg}


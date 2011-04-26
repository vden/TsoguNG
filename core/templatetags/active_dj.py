# -*- coding: utf-8 -*-

from django import template
from core.views import get_object_by_url
from django.contrib.auth.models import User

register = template.Library()

@register.inclusion_tag('active_dj.html')
def active_dj():
    root = get_object_by_url("/")
    cfg = root.config().get('active_dj_')
    avatar = ''
    name = ''
    if cfg:
        profile = User.objects.get(username=cfg)
        try:
            avatar = profile.get_profile().avatar.url()
        except:
            pass
        name = u"%s %s"%(profile.first_name, profile.last_name)
    return {'avatar': avatar, 'name': name}

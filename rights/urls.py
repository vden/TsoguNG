# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('tsogung.rights.views',
	(r'go/(?P<app_uuid>[0-9a-fA-F\-]+)/$','go'),
	(r'go_public/(?P<app_uuid>[0-9a-fA-F\-]+)/$','go_public'),
	(r'token/(?P<token>[0-9a-fA-F\-]+)/$','token'),
)

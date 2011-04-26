# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
	(r'^photos/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.PHOTOS_ROOT}),
	(r'^files/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.FILE_ROOT}),
	(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

	(r'^portal/(?P<action>.*)/$', 'tsogung.core.views.dispatcher', {'path_info':''}),

	(r'^act/(?P<action>.*)/$', 'tsogung.core.views.dispatcher', {'path_info': '/'}),
	(r'^(?P<path_info>.*)/act/(?P<action>.*)/$', 'tsogung.core.views.dispatcher'),

	(r'^(?P<path_info>.*)/RSS/(?P<type_name>.*)/$','tsogung.core.views.rss_dispatcher'),
	(r'^RSS/(?P<type_name>.*)/$','tsogung.core.views.rss_dispatcher', {'path_info': '/'}),

	(r'^(?P<path_info>.*)/image/(?P<size>.*)/(?P<crop>.?)/$','tsogung.core.views.thumbnail_dispatcher'),

	(r'^$', 'tsogung.core.views.dispatcher', {'path_info': '/','action':'view'}),
	(r'^(?P<path_info>.*)/$', 'tsogung.core.views.dispatcher', {'action':'view'}),
)

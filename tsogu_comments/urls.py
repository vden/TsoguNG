# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('tsogung.tsogu_comments.views',
	(r'^add/$', 'add'),
	(r'^moderation/$', 'moderation'),
	(r'^moderation/(?P<action>\w+)/$', 'moderation_action'),
)

# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('tsogung.userprofile.views',
	(r'^$', 'index'),
	(r'^update/$', 'update'),
	(r'^edit/$', 'edit'),
	(r'^send_email_confirm/$', 'send_email_confirm'),
	(r'^student_status_confirm/$', 'student_status_confirm'),
	(r'^email_confirm/(?P<user_id>\d+)/(?P<code>[0-9a-fA-F\-]+)/$','email_confirm'),
#	(r'token/(?P<token>[0-9a-fA-F\-]+)/$','token'),
)

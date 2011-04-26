from django.conf.urls.defaults import *
from core.restapi_collections import *
from django.contrib import admin
from django.conf import settings
admin.autodiscover()

urlpatterns = patterns('',
	(r'^media/django_extensions/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.EXTENSIONS_MEDIA_ROOT, 'show_indexes': True}),
	(r'^media/js/tinymce/connector/python/', include('tinymce.images.urls')),
	(r'^media/js/tiny_mce/connector/python/', include('tinymce.images.urls')),
	(r'^admin/', include(admin.site.urls)),
	(r'^comments/', include('tsogung.tsogu_comments.urls')),
	(r'^captcha/', include('captcha.urls')),
	(r'^rights/', include('tsogung.rights.urls')),
	(r'^userprofile/', include('tsogung.userprofile.urls')),
)

urlpatterns += patterns('',
	url(r'^xml/news/(.*?)/?$', xml_news_resource),
	url(r'^xml/page/(.*?)/?$', xml_page_resource),
	url(r'^xml/photo/(.*?)/?$', xml_photo_resource),
	url(r'^xml/file/(.*?)/?$', xml_file_resource),
	url(r'^xml/event/(.*?)/?$', xml_event_resource),
	url(r'^xml/link/(.*?)/?$', xml_link_resource),
	url(r'^xml/dissertation/(.*?)/?$', xml_dissertation_resource),
)

urlpatterns += patterns('',
	(r'^', include('tsogung.core.urls')),
)

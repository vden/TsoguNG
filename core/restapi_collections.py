# -*- coding: utf-8 -*-

from django_restapi.model_resource import Collection
from django_restapi.responder import JSONResponder
from django_restapi.authentication import HttpDigestAuthentication, HttpBasicAuthentication
from core.types import *

xml_news_resource = Collection(
	queryset = News.objects.all(),
	permitted_methods = ('GET', 'POST', 'PUT', 'DELETE'),
	responder = JSONResponder(paginate_by=10),
)

xml_page_resource = Collection(
	queryset = Page.objects.all(),
	permitted_methods = ('GET', 'POST', 'PUT', 'DELETE'),
	responder = JSONResponder(paginate_by=10)#
)

xml_photo_resource = Collection(
	queryset = Photo.objects.all(),
	permitted_methods = ('GET', 'POST', 'PUT', 'DELETE'),
	responder = JSONResponder(paginate_by=10)#
)

xml_file_resource = Collection(
	queryset = File.objects.all(),
	permitted_methods = ('GET', 'POST', 'PUT', 'DELETE'),
	responder = JSONResponder(paginate_by=10)#
)

xml_event_resource = Collection(
	queryset = Event.objects.all(),
	permitted_methods = ('GET', 'POST', 'PUT', 'DELETE'),
	responder = JSONResponder(paginate_by=10)#
)

xml_link_resource = Collection(
	queryset = Link.objects.all(),
	permitted_methods = ('GET', 'POST', 'PUT', 'DELETE'),
	responder = JSONResponder(paginate_by=10)#
)

xml_dissertation_resource = Collection(
	queryset = Dissertation.objects.all(),
	permitted_methods = ('GET', 'POST', 'PUT', 'DELETE'),
	responder = JSONResponder(paginate_by=10)#
)

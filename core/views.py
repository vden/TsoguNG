# -*- coding: utf-8 -*-

from django.http import HttpResponse
from core.portal.utils import get_object_by_url
from core import REGISTRUM
from core.portal.exceptions import Http404, Http302

def dispatcher(request, path_info, action, redirect=False):
	if redirect:
		raise Http302(path_info)

	if path_info:
		obj = request.main_object
		objectaction = REGISTRUM['types'][obj.get_class_name()]['actions'].get(action)
		if not objectaction: raise Http404(u'Запрашиваемый action (%s) в системе не зарегистрирован.'%action)
		func = getattr(obj, action)

	else:
		act = REGISTRUM['actions'].get('portal_%s'%action)
		if not act: raise Http404(u'Запрашиваемый action (%s) в системе не зарегистрирован.'%action)
		func = act['function']
	return func and func(request=request) or HttpResponse(u'PASS')

def rss_dispatcher(request, path_info, type_name):
	"""
	конфиглеты:
	rss_show ::= True|False, показывать ли на этой странице ленту сразу же
	rss_link ::= <url>, показывать по ссылке <.../RSS> ленту для этого объекта вместо текущего
	rss_type ::= CLASS_NAME, по умолчанию (в случае с rss_show) показывать опр. тип
	"""

	from django.contrib.syndication.views import feed

	from core.feeds import ObjectFeed
	request.rss_type_name = type_name

	page = get_object_by_url(path_info)
	path_info = page.config().get('rss_link',  path_info)
	request.config = page.config()

	return feed(request, url = "default/%s"%path_info, feed_dict = {'default': ObjectFeed} )

def thumbnail_dispatcher(request, path_info, size, crop):
	"""
	возвращает тумбнейлы
	формат вызова адреса: /news/folder/my_image/image/medium/1/ --
	картинка /news/folder/my_image размера 160х160, кропнутая
	"""

	THUMB_SIZE = {
		'tiny': (48, 48),
		'small': (80, 80),
		'medium': (160, 160),
		'big': (240, 240),
		'large': (320, 320),
		'extralarge': (640, 640)
		}

	dsize = THUMB_SIZE.get(size, (160,160))
	obj = get_object_by_url(path_info)

	if obj.get_class_name() not in ['Photo','VideoFile', 'News']: raise Http404

	if str(crop) != "0":
		img = obj.thumbnail_cropped(dsize)
	else:
		img = obj.thumbnail_resized(dsize)

	resp = HttpResponse(mimetype="image/jpeg")
	img.save(resp, "JPEG")
	return resp

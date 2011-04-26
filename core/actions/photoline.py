# -*- coding: utf-8 -*-

from core.portal.register import portalaction
from core.portal.render import render_to_portal
from core.views import get_object_by_url
from core.models import BaseObject
import random

@portalaction(verbose_name=u'Фотокалейдоскоп')
@render_to_portal(template='actions/photogallery.html')
def photoline(request):
	result = BaseObject.nodes()(types=['News'], sort_fields=['-date_published'], states=[u'опубликовынный',u'на главной']).all()[:100]

	all_imgs = []
	for x in result:
		all_imgs.extend( x.get_images() )

	format = request.GET.get("format", "medium")
	if format != "small":
		format = "medium"
		x = y = 160
		count = 25
	else:
		x =  y = 80
		count = 70

	print "EEE", len(all_imgs), count
	imgs = random.sample(all_imgs, count)

	return { 'imgs': imgs, 'format': format, 'x': x, 'y': y }

# -*- coding:utf-8 -*-

from django import template
register = template.Library()

from banners.models import BannerGroup, Banner
from datetime import datetime
from django.db.models import Q
from django.core.cache import cache
from random import shuffle

@register.inclusion_tag('banners.html')
def banners(request, group, width=None, height=None, vertical=False):
	now = datetime.now()
	
	if not hasattr( request, 'banners' ): request.banners = {}
	exclude_ids = request.banners.get(group, [])

	# для того, чтобы "инциализировать" пустую группу, но и не затереть существующую
	request.banners[group] = exclude_ids
	bgroup = BannerGroup.objects.get( name=group )
	count = bgroup.count
	
	banners = bgroup.banner_set.filter( effective_date__lt = now )\
			  .filter( Q(expire_date__isnull = True) | Q(expire_date__gt = now) )\
			  .exclude( id__in=exclude_ids )\
			  .order_by('?')[:count]
	request.banners[group].extend( [ x.id for x in banners ] )

	# TODO: сделать, чтобы при меньшем числе полученных баннеров, система отдавала какие-нибудь баннеры
	# из уже показанных. или не надо этого делать... непонятно.

	return { 'banners': banners, 'group': group, 'w': width, 'h': height, 'vert': bool(vertical) }

@register.inclusion_tag('banners.html')
def cache_banners(request, group, width=None, height=None, vertical=False):
	key = "bannerscachett_%s"%group
	data = cache.get(key)

	if not data:
		now = datetime.now()
		bgroup = BannerGroup.objects.get( name=group )
		count = bgroup.count
		banners = [x for x in bgroup.banner_set.filter( effective_date__lt = now )\
				.filter( Q(expire_date__isnull = True) | Q(expire_date__gt = now) )]
		cache.add(key, (count, banners), 4*60*60)
	else:
		count, banners = data

	shuffle(banners)
	banners = banners[:count]

	return { 'banners': banners, 'group': group, 'w': width, 'h': height, 'vert': bool(vertical) }


@register.inclusion_tag('text_banners.html')
def text_banners(request, group):
	now = datetime.now()
	
	if not hasattr( request, 'text_banners' ): request.text_banners = {}
	exclude_ids = request.text_banners.get(group, [])

	# для того, чтобы "инциализировать" пустую группу, но и не затереть существующую
	request.text_banners[group] = exclude_ids
	bgroup = BannerGroup.objects.get( name=group )
	count = bgroup.count
	
	banners = bgroup.textbanner_set.filter( effective_date__lt = now )\
			  .filter( Q(expire_date__isnull = True) | Q(expire_date__gt = now) )\
			  .exclude( id__in=exclude_ids )\
			  .order_by('?')[:count]
	request.text_banners[group].extend( [ x.id for x in banners ] )

	# TODO: сделать, чтобы при меньшем числе полученных баннеров, система отдавала какие-нибудь баннеры
	# из уже показанных. или не надо этого делать... непонятно.

	return { 'banners': banners, 'group': group }

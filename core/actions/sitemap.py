# -*- coding: utf-8 -*-

from core.portal.register import portalaction
from core.portal.render import render_to_portal
from core.models import BaseObject

@portalaction(verbose_name=u'Карта портала')
@render_to_portal(template='actions/sitemap.html', columns=('b', 'c'))
def sitemap(request):
	from core.types.support import State
	from core.types.link import Link

	public = State.objects.get(name=u'опубликованный')
	nodes_params = dict(types=['Link', 'Page'], sort_fields=['position'], states=[public], not_browse=False)

	def set_children(parents, depth=0):
		from collections import defaultdict
		children = defaultdict(list)
		objects = BaseObject.nodes(**nodes_params).parents(*parents).query_set.only('id', 'slug', 'parent', 'title', 'type')
		while depth:
			depth -= 1
			set_children(objects, depth)
		for object in objects:
			children[object.parent_id].append(object)
			object.type == 'Link' and links.append(object.id)
		for parent in parents:
			parent.children = children[parent.id]

	frontpage = BaseObject.objects.filter(parent__id=None).only('id')[0]
	objects = BaseObject.nodes(**nodes_params).parents(frontpage).query_set.only('id', 'slug', 'parent', 'title', 'type')
	links = [object.id for object in objects if object.type == 'Link']
	set_children(objects, depth=1)
	links = Link.objects.only('url').in_bulk(links)
	return {'sitemap': objects, 'links': links}

# -*- coding: utf-8 -*-

def trash(object, request):
	"""
		PageTemplate trash -- корзина
		Возвращает список объектов parent-ом которых она является.
		TODO: добавить paginator
	"""
	from core.models import BaseObject
	objects = BaseObject.nodes(parents=[object.id], foruser=True, sort_fields=['-date_modified'])
	if not request.user.is_superuser:
		objects = objects.authors(request.user)
	return {'objects':objects.all()}

def example_custom_template(object, request):
    """
    В метод передаются сам объект шаблона, наследник от BaseObject,
    и объект запроса request.
    """
    ip = request and request.META['REMOTE_ADDR'] or "I don't know your IP, sir!"
    return {'ip': ip}

def static_menu_navigation(object, request):
    return {}

def page_content(object, request):
	from core.models import BaseObject
	try:
		reference_object = BaseObject.objects.get(id=object.config()['reference_object_id']).direct_cast()
	except Exception, E:
		reference_object = E
	return {'reference_object':reference_object}

def wow_news(object, request):
	return {}

def banners_top_right(obj, request):
    return {'path': request.path }

def bic_banners_left(obj, request):
	return {'path': request.path }

def banners_left(obj, request):
    return {'path': request.path }

def plain_menu_navigation(object, request):
	object = request.main_object
	if object.config().has_key('menu_for_page'):
		from core.views import get_object_by_url
		object = get_object_by_url(object.config()['menu_for_page'])
	next_nodes = object.get_child_nodes_menu()
	if next_nodes:
		menu = next_nodes
	else:
		menu = object.parent and object.parent.get_child_nodes_menu() or []
	return {'menu':menu, 'obj':object, 'orig_obj':request.main_object}

def media_tsogu(object, request):
    return {}

def calendar(object, request):
    return {}

def search_box(object, request):
    return {'search_word': request.GET.get('search_word', '')}

def announcements(object, request):
    return {}

def banners_right(object, request):
    return {'path': request.path}

# Section Голосования
def get_polls(object):
    from core.types import Poll
    if not 'poll_tags_' in object.config().keys():
        p = Poll.active().filter(state__name=u'опубликованный').order_by('-date_published')
    else:
        p = Poll.active().filter(state__name=u'опубликованный',
            tags__name__in=[u'%s'%x for x in object.config()['poll_tags_'].split(',')]).order_by('-date_published')
    return p
#return None

def portlet_poll(object, request):
    q = get_polls(request.main_object)
    return {'poll': q and q[0] or None}

def polls(object, request):
    return {'polls':get_polls(request.main_object)}
# endSection

def dissers(object, request):
    return {}

from core.decorators import cache_on_param

#@cache_on_param(params=[], prefix=u'schedule', time=4*60*60)
def schedule(object, request, **kwargs):
	from utils.schedule import get_institutes
	from datetime import date
	today = date.today()
	offset = 0
	week = [u'четная',u'нечетная']
	wk = u'%s неделя' % week[(today.isocalendar()[1]+offset)%2]
	return {'institutes':get_institutes(), 'wk':wk}

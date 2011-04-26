# -*- coding:utf-8 -*-

from core.portal.register import portalaction
from core.portal.render import render_ajax, render_to_portal
from core.models import BaseObject

class RequestMethodorDataError(Exception):
	pass

def get_search_results(search_word):
	from core.types.support import State
	states_ids = State.objects.filter(name__in = ['опубликованный','на главной']).values_list('id', flat=True)
	try:
		lst = [x.direct_cast() for x in BaseObject.objects.search(search_word) if x.state_id in states_ids]
		return lst
	except TypeError, E:
		return []

@portalaction(verbose_name=u'Поиск')
@render_to_portal(template='actions/search_results.html')
def search(request):
	""" главная функция action-модуля """

	if request.method == 'GET' and request.GET.has_key('search_word'):
		return {'search_results':get_search_results(request.GET.get('search_word',' ')) }
	else:
		raise RequestMethodorDataError()


@portalaction(verbose_name=u'Поиск')
@render_ajax(type='html', template='custom/search_results_ajax.html')
def lookup_search(request):
	lst = get_search_results(request.POST.get('search_word', ' '))
	groups = {}

	import itertools
	data = sorted(lst, key=lambda x: x.get_class_name_i18n())
	for k, g in itertools.groupby(data, lambda x: x.get_class_name_i18n()):
		groups[unicode(k)] = [x for x in list(g)][:4]

	return {'groups': groups}

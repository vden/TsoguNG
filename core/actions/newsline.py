# -*- coding: utf-8 -*-

from core.portal.register import portalaction
from core.portal.render import render_to_portal, render_as_redirect

@portalaction(verbose_name=u'Новостной архив')
@render_to_portal(template='actions/content_news.html', columns=('a', 'b'))
def newsline(request):
	from core.types import News
	from core.types.support import Tag
	from core.models import BaseObject
	from core.views import get_object_by_url
	from django import forms
	from core.forms import CalendarDateField
	from django.contrib.admin import widgets as admin_widgets
	from django.core.paginator import Paginator

	class NewsForm(forms.Form):
		begin_date = CalendarDateField(label=u'С', required=False)
		end_date = CalendarDateField(label=u'По', required=False)
		tags = forms.MultipleChoiceField(widget=admin_widgets.FilteredSelectMultiple(u'метки', 0),\
					required=False, choices=[(x.id,x.name) for x in Tag.objects.all()])


	news = News.objects.filter(state__name__in=[u'опубликованный',u'на главной']).order_by('-date_published')
	form = NewsForm(request.GET)

	if form.is_valid():
		begin_date = form.cleaned_data['begin_date'] or ''
		if begin_date:
			news = news.filter(date_published__gte = begin_date)

		end_date = form.cleaned_data['end_date'] or ''
		if end_date:
			news = news.filter(date_published__lte = end_date)

		tags = ''
		if form.cleaned_data['tags']:
			tags = ''.join(['&tags=%s'%x for x in form.cleaned_data['tags']])
			news = news.filter(tags__in=form.cleaned_data['tags']).distinct()

	else:
		raise Exception('Form error')

	pages = Paginator(news, 50)
	try:
		cur_page = int(request.GET.get('page', '1'))
	except ValueError:
		cur_page = 1
	page = pages.page(cur_page)

	return {'form':form, 'pages':pages, 'cur_page':cur_page, 'page':page, 'query':'begin_date=%s&end_date=%s%s'%(begin_date and begin_date.strftime('%d.%m.%Y'), end_date and end_date.strftime('%d.%m.%Y'), tags)}

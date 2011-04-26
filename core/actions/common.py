# -*- coding: utf-8 -*-

from core.portal.register import portalaction
from core.portal.render import render_to_portal, render_as_redirect, render_ajax

@portalaction(verbose_name=u'Отчёт по обновлению страниц портала', category='workspace')
@render_to_portal(template='actions/report_update.html', columns=('a', 'b'))
def report_update(request):
	from rights.models import Responsibility
	ordering = {'1': 'base_object__title',
			'2': 'user',
			'3': 'position',
			'4': 'telephone',
			'5': 'base_object__date_created',
			'6': 'base_object__date_modified'}
	order_by = request.GET.get('order_by', '1')
	direction = {'1':True, '0':False}.get(request.GET.get('direction', '1'), True)
	order_field = '%s%s'%(('-','')[direction], ordering.get(order_by, ordering['1']))
	resp = Responsibility.objects.all().order_by(order_field)
	return {'resp':resp, 'order_by':('1',order_by)[order_by in ordering], 'direction':direction}

@portalaction(verbose_name=u'Настройки портала', category='user', condition='isStaff')
@render_as_redirect()
def admin(request):
	return '/admin/'

@portalaction(verbose_name=u'Профиль', category='user', condition='isAuthenticated')
@render_as_redirect()
def profile(request):
	return '/userprofile/'

@portalaction(verbose_name=u'Почта', category='user', condition='True')
@render_as_redirect()
def webmail(request):
	return 'http://webmail.tsogu.ru'

@portalaction(verbose_name=u'Выход', category='user', condition='isAuthenticated')
@render_to_portal(template='actions/logout.html')
def logout(request):
	from django.contrib.auth.views import logout
	logout(request)
	return {}

@portalaction(verbose_name=u'Журнал ошибок', condition='isStaff')
@render_to_portal(template='action/logs.html')
def logs(request):
	from core.types import Log
	return {'logs': Log.objects.all().order_by('-date')[:100]}

@portalaction(verbose_name=u'REGISTRUM', category='user', condition="isSuperuser")
@render_to_portal(template='actions/registrum.html')
def registrum(request):
	from core import REGISTRUM
	return {'REGISTRUM':REGISTRUM}

@portalaction(verbose_name=u'Редакторский лист', category='user', condition="u'reviewer' in groups")
@render_to_portal(template='actions/reviewer_list.html', columns=('a', 'b'))
def reviewer_list(request):
	from core.models import BaseObject
	objs = BaseObject.nodes(states = [u'на редактировании'], sort_fields = ['date_modified']).all()
	return {'obj_list':objs}


@portalaction(verbose_name=u'Общая статистика', category='workspace', condition='isSuperuser')
@render_to_portal(template='actions/statistic.html')
def statistic(request):
	from core.types import Page, News, Link, Photo, File, AudioFile, VideoFile, PageTemplate, Event, Poll, Dissertation, Post
	import os

	context = {}
	context['events_qty'] = Event.objects.count()
	context['links_qty'] = Link.objects.count()
	context['photos_qty'] = Photo.objects.count()
	context['audios_qty'] = AudioFile.objects.count()
	context['videos_qty'] = VideoFile.objects.count()
	context['polls_qty'] = Poll.objects.count()
	context['dissers_qty'] = Dissertation.objects.count()
	context['posts_qty'] = Post.objects.count()
	context['news_qty'] = News.objects.count() - context['events_qty']
	context['pages_qty'] = Page.objects.count() - context['events_qty'] - context['news_qty']
	context['files_qty'] = File.objects.count() - context['audios_qty'] - context['videos_qty']
	context['pts_qty'] = PageTemplate.objects.count()
	s = os.statvfs('/var/web/tsogung/')
	context['free_space'] = (s.f_bsize * s.f_bavail)
	return context

@portalaction(verbose_name=u'Корзина', category='user', condition='isAuthenticated')
@render_as_redirect()
def trash(request):
	return '/trash/'

@portalaction(verbose_name=u'Расписание.Группы')
@render_ajax(type="json")
def schedule_groups(request):
	from utils.schedule import get_groups
	id_inst = request.GET.get('inst', None)

	try:
		id_inst = int(id_inst)
	except:
		return {'error': 'Institute id error'}

	return {'groups':get_groups(id_inst)}

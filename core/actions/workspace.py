# -*- coding:utf-8 -*-

from core.portal.register import portalaction
from core.portal.render import render_to_portal
from core import REGISTRUM
from rights import has_access
from utils.snippets import http_auth_request
import simplejson

@portalaction(verbose_name=u'Рабочая зона', category='user', condition='isAuthenticated')
@render_to_portal(template='actions/workspace.html')
def workspace(request):
	""" главная функция action-модуля"""
	available_applications = get_available_apps(request)
	available_types = get_available_types(request)
	try:
		jobs = get_jobs(request.user)
	except:
		jobs = []
	return {'types': available_types, 'apps': available_applications,
				'ws_actions': get_actions(request), 'last_objects': get_latest_objects(request.user),
				'external_apps':get_available_appss(request),
				'ownership':get_ownership(request.user),
				'schedule': get_schedule(request.user),
				'jobs': jobs }

def get_ownership(user):
	from rights.models import DelegateRight
	return [dr.base_object for dr in DelegateRight.objects.filter(user=user, group__name='Owner').select_related('base_object')]

def get_available_apps(request):
	sid = request.session.session_key
	return [#{'name': u'АИС «Контингент студентов»', 'url': u'http://std.tsogu.ru/bin/student/student.cgi'},
			#{'name': u'АИС «Аспирант»', 'url': u'http://app.tsogu.ru/aspirant'},
			{'name': u'АИС «Электронное расписание»', 'url': u'http://app.tsogu.ru/shedule/'},
			{'name': u'АИС «Отчетность по НИР»', 'url':u'http://std.tsogu.ru/nir/'},
#			{'name': u'Полнотекстовая БД (просмотр)', 'url': u'http://app.tsogu.ru/lib/?sessionid=%s'%sid} ]
			]

def get_jobs(user):
	student_id = user.get_profile().student_id
        [student_data] = simplejson.load(http_auth_request('http://api.tsogu.ru/students/student/%s/' % student_id, 'robot_api', 'oocei4Ga'))
	data = http_auth_request('http://jobs.tsogu.ru/api/vacbyspec/%s/' % student_data['speciality']['id'], 'nimda', 'OoGhail9')
	return simplejson.load(data)

def get_available_appss(request):
	from rights.models import Application, UserGroups
	apps = [x.application for x in UserGroups.objects.filter(user=request.user,application__public=False)]
	apps.extend([x for x in Application.objects.filter(public=True)])
	return apps

def get_available_types(request):
	from core.views import get_object_by_url
	from django.contrib.auth.models import Permission
	from django.contrib.contenttypes.models import ContentType
	available_types = []

	for type in REGISTRUM['workspace'].values():
		obj = get_object_by_url(type['default_place'])
		content_type = ContentType.objects.get_for_model(REGISTRUM['types'][type['type']]['cls'])
		permission = Permission.objects.get(codename='insert', content_type=content_type)

		if has_access(request.user, permission, obj):
			available_types.append(type)

	return available_types

def get_schedule(user):
	pass
"""
	import utils.schedule as schedule
	from datetime import datetime

	try:
		edu_group = user.get_profile().edu_group
	except:
		return None
	gcode = schedule.get_group_code(edu_group)
	gtable = schedule.get_timetable(gcode)

	now = datetime.today()
	wn=int(now.strftime('%W'))

	if not isinstance(gtable, list):
		return None
	else:
		return {'gtable': gtable, 'edu_group': edu_group, 'gcode': gcode, 'week': (1-wn%2), 'day': now.day}
"""

def get_latest_objects(user):
	from core.models import BaseObject
	from django.contrib.auth.models import User

	f = BaseObject.objects.filter(author=user).order_by('-date_modified')[:15]
	return [x.direct_cast() for x in f]

def get_actions(request):
	res = [{'name': act['verbose_name'], 'url': act['url']}
				for act in REGISTRUM['actions'].values()
				if act['category'] == 'workspace' and has_access(request.user, 'portal_%s'%act['funcname'])]
	return res

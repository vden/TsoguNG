# -*- coding: utf-8 -*-
from django.http import Http404, HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
import logging

def check_permission (codename, verbose_name, obj=None):
	"""
		Проверяет наличие разрешения, при необходимости создаёт его.
		Возвращает True если разрешение создано, False если оно уже есть.
		codename -- codename разрешения
		verbose_name -- нормальное человеческое название, функция сохраняет его в запрашиваемое разрешение
		obj -- объект портала, нужен для того, что бы получить content_type, по умолчанию используется portal content_type
	"""
	if obj:
		content_type = ContentType.objects.get_for_model(obj)
	else:
		content_type = ContentType.objects.get(app_label='tsogung', model='portal')
	permission, new = Permission.objects.get_or_create(codename=codename, content_type=content_type,
			defaults={'name': verbose_name})
	if new: logging.warn(u'CREATE PERMISSION %s(%s): %s'%(codename, verbose_name, content_type))
	elif permission.name != verbose_name:
		permission.name = verbose_name
		permission.save()
	return new

def has_access_old(user, action, location=None, app='tsogung'):
	"""
		Итак, проверка прав доступа
		@return: True в положительном исходе, False при отрицательном
		@var user: объект пользователя
		portal -- gps, local -- not gps (gps -- global permission)
		todo: добавить подробный комментарий
	"""
	#logging.warn("DEPRECATED HAS_ACCESS_OLD")
	logging.debug('HAS_ACCESS\n\t(user,action,location):%s %s %s'%(user,action,location and location.id))
	from rights.models import ObjectPermissions, DelegateRight
	from core.models import BaseObject

	content_type=permission=owner_group=None
	try:
		content_type = ContentType.objects.get(app_label=app, model=(location and 'local' or 'portal'))
		permission = Permission.objects.get(codename=action, content_type=content_type)
		owner_group = Group.objects.get(name=u'Owner')
	except:
		logging.error('HAS_ACCESS\n\t(user,action,location):%s %s %s\n\t(content_type, permission, owner_group):%s %s %s'%(user,action,location and location.id, content_type, permission, owner_group))
		return False

	if user.is_superuser:
		return True

	if location and not location.id: location = location.parent
	groups = set(Group.objects.filter(name=u'Guest').values_list('id', flat=True))
	if not user.is_anonymous():
		groups.update(Group.objects.filter(name=u'Member').values_list('id', flat=True))
		groups.update(user.groups.values_list('id', flat=True))
		if location:#not gps
			if location.author == user:
				return True
			path = BaseObject.objects.look2root(location.id, True)['path']
			if BaseObject.objects.filter(id__in=path, author=user).values('id')[:1]:
				return True
			groups.update(DelegateRight.objects.filter(base_object__id__in=path, user=user).values_list('group', flat=True))
			if owner_group.id in groups:
				return True

	return bool(permission.group_set.filter(id__in=groups).values('id')[:1] or \
			not user.is_anonymous() and \
			permission.user_set.filter(username=user.username).values('id')[:1])

def has_access(user, permission, location=None):
	"""
		Итак, проверка прав доступа
		@return: True в положительном исходе, False при отрицательном
	"""
	from rights.models import ObjectPermissions, DelegateRight
	from core.models import BaseObject

	content_type=owner_group=None
	try:
		if not isinstance(permission, Permission):
			if location:
				content_type = ContentType.objects.get_for_model(location)
			else:
				content_type = ContentType.objects.get(app_label='tsogung', model='portal')
			permission = Permission.objects.get(codename=permission, content_type=content_type)
		owner_group = Group.objects.get(name=u'Owner')
	except:
		logging.error('HAS_ACCESS\n\t(user, action, content_type ,location):%s %s %s %s'%(user,getattr(permission, 'codename', ''), getattr(permission, 'content_type', ''), location and location.id))
		return False
	logging.debug('HAS_ACCESS\n\t(user, action, content_type ,location):%s %s %s %s'%(user,getattr(permission, 'codename', ''), getattr(permission, 'content_type', ''), location and location.id))

	if user.is_superuser:
		return True

	if location and not location.id: location = location.parent
	groups = set(Group.objects.filter(name=u'Guest').values_list('id', flat=True))
	if not user.is_anonymous():
		groups.update(Group.objects.filter(name=u'Member').values_list('id', flat=True))
		groups.update(user.groups.values_list('id', flat=True))
		if location:#not gps
			if location.author == user:
				return True
			path = BaseObject.objects.look2root(location.id, True)['path']
			if BaseObject.objects.filter(id__in=path, author=user).values('id')[:1]:
				return True
			groups.update(DelegateRight.objects.filter(base_object__id__in=path, user=user).values_list('group', flat=True))
			if owner_group.id in groups:
				return True

	return bool(permission.group_set.filter(id__in=groups).values('id')[:1] or \
			not user.is_anonymous() and \
			permission.user_set.filter(username=user.username).values('id')[:1])

def go(request, app_uuid):
	from models import Application, Token
	app = get_object_or_404(Application, uuid=app_uuid)
	return HttpResponseRedirect(u'%s%s'%(app.link,Token.set(request.user,app)))

def go_public(request, app_uuid):
	from models import Application, Token, UserGroups
	app = get_object_or_404(Application, uuid=app_uuid)
	if not app.public:
		return HttpResponse(u'Permission deny')

	if not request.user.get_profile().is_email_confirmed:
		return HttpResponse(u'Confirm your email or use direct link http://elib.tsogu.ru/')

	try:
		ug = UserGroups.objects.get(user=request.user, application=app)
	except:
		ug = UserGroups(user=request.user, application=app, groups=u' ')
		ug.save()

	return HttpResponseRedirect(u'%s%s'%(app.link,Token.set(request.user,app)))

def token(request, token):
	from models import Token
	return HttpResponse(Token.check(token))


# -*- coding: utf-8 -*-

"""
	Регистраторы объектов и методов.

	@author: Vlasov Dmitry
	@contact: scailer@tsogu.ru
	@organization: TSOGU
	@status: функционирует
	@version: 1.0
"""

from core import REGISTRUM
import logging
import inspect
from functools import wraps
from rights import check_permission, has_access
from core.portal.exceptions import Http403

def register_action(type, name, verbose_name, function, category=None, condition="True"):
	codename = '%s_%s'%(type,name)
	if codename in REGISTRUM['actions']:
		logging.warning('REGISTER ACTION %s already registered'%codename)
	REGISTRUM['actions'][codename] = {'verbose_name':verbose_name,
			'function':function, 'funcname':name, 'type':type,
			'url':'/portal/%s/'%name,
			'condition':condition, 'category':category}
	logging.info('REGISTER ACTION %s'%codename)

def register_type(cls, base=None, user=True, verbose_name=u''):
	if not verbose_name:
		verbose_name = getattr(cls._meta, 'verbose_name', u'')
		actions = {}
	for member_name in dir(cls):
		try:
			member = getattr(cls, member_name)
			if inspect.ismethod(member) and getattr(member, 'is_objectaction', False):
				actions[member_name] = {'verbose_name': member.verbose_name,
										'name': member_name,
										'category': member.category}
				check_permission(member_name, member.verbose_name, cls)
		except: pass
	REGISTRUM['types'][cls.__name__] = {'cls':cls, 'verbose_name':verbose_name,
			'user':user, 'base':base, 'actions': actions}
	logging.info('REGISTER TYPE %s'%cls.__name__)

def register_workspace(cls, verbose_name, default_place, description):
	REGISTRUM['workspace'][cls.__name__] = {'verbose_name': verbose_name, 'type':cls.__name__,
			'default_place': default_place, 'description': description}

def objectaction(verbose_name, category=None, check_access=True):
	"""
		Декoратор, регистрирующий методы объекта.
		verbose_name -- понятное для всех название
		category -- категория action-а (например для того что бы знать показывать или нет в табах..)
		check_access -- флаг необходимости проверки прав доступа перед выполнением действия.
	"""
	def func(fn):
		fn.is_objectaction = True
		fn.verbose_name = verbose_name or u''
		fn.category = category
		@wraps(fn)
		def call(*args, **kw):
			location = args[0]
			request = kw.get('request') or args[1]
			if check_access and location.id and not has_access(request.user, fn.__name__, location):
				raise Http403
			return fn(*args, **kw)
		return call
	return func

def portalaction(*args, **kw):
	if kw.has_key('name'):
		raise Exception(u'Remove name from objectaction decorator')
	kw['type'] = 'portal'

	def func(fn):
		@wraps(fn)
		def call(*cargs, **ckw):
			request = ckw.get('request') or cargs[0]
			if not has_access(request.user, 'portal_%s'%fn.__name__):
				raise Http403
			return fn(*cargs, **ckw)
		kw['name'] = fn.__name__
		kw['function'] = call
		register_action(**kw)
		check_permission('portal_%s'%kw['name'], kw.get('verbose_name', kw['name']))
		return call
	return func

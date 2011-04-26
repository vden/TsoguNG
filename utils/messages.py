# -*- coding: utf-8 -*-

from django.http import HttpResponseServerError

try:
	from threading import local
except ImportError:
	from django.utils._threading_local import local


class PortalMessage(unicode):
	""" Сообщение портала """
	color = 'black'
	type = 'message' #{'error','message','warning','crash'}
	default_color = {'error':u'red','message':'black','warning':'black','crash':'red','complete':'blue'}
	default_verb = {'error':u'Ошибка:','message':u'','warning':u'Внимание:','crash':u'Авария:','complete':u'Успешно завершено:'}
	is_global = False

	def set_property(self, color=None, type='message'):
		self.color = color and color or self.default_color[type]
		self.type = type
		return self

	def verb_type(self):
		return self.default_verb[self.type]


class PortalMessageSlot(list):
	""" Обработчик сообщений портала """

#	def all(self):
#		getattr(self._thread_locals, 'messages')
#
#	def get_locale(self):
#		return [x for x in self.all() if not x.is_global]
#
#	def get_global(self):
#		return [x for x in self.all() if x.is_global]
#
#	def is_global_error(self):
#		return bool([x for x in self.all() if (x.is_global and x.type in ['error','crash'])])
#
#	def set(self, mes):
#		print "EEE",mes
#		try: self._thread_locals.messages.append(mes)
#		except: raise Exception(u'Не удалось поместить сообщение в локальный тред')
#		print "QQQ",self._thread_locals.messages

class MessageType(object):
	def __init__(self, slug, color, name):
		self.slug = slug
		self.color = color
		self.name = name

message_types = {
		'error':	MessageType('error','red',u'Ошибка'),
		'message':	MessageType('message','green',u'Сообщение'),
		'warning':	MessageType('warning','black',u'Внимание'),
		'crash':	MessageType('crash','red',u'Авария'),
		'complete':	MessageType('complete','blue',u'Успешно завершено'),
		}

class Message(object):
	def __init__(self, code, text, type=message_types['message']):
		self.code = code
		self.text = text
		self.type = type
	
	def __unicode__(self):
		return u'%s %s'%(self.type.name, self.text)

	def __str__(self):
		return self.__unicode__()

class PortalMessage2(object):
	def __init__(self, id=None):
		pass

class QueryMessage(object):
	def __init__(self):
		pass

class ServerMessage(object):
	pass

class SessionMessage(object):
	pass

class MessagePool(object):
	"""
		global = 
		query = 
		session = 
	"""
	pass


class LocalMessageSlot(object):
	def __init__(self, data):
		pass


	def set(self, message):
		pass
		


class GlobalMessageSlot(list):
	pass

class SessionMessageSlot(list):
	pass

class MessageSlot(object):
	local_slot = None
	global_slot = None
	session_slot = None

	def __init__(self):
		""" Global init """
		pass

	def __call__(self):
		""" Local init """
		pass




global MES_loaded
MES_loaded = False

if not MES_loaded:
	dbpool = MessageSlot()
	MES_loaded = True


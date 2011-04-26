# -*- coding: utf-8 -*-
from django.core.cache import cache
try: import hashlib
except: import md5 as hashlib

# Простой кеш, сохраняет по одному из параметров функции, инвалидирует по таймауту
class simple_cache(object):
	def __init__(self, time=60*60):
		print "CALL simple_cache.__init__"
		self.time = time

	def __call__(self, f):
		def wrapper(*args, **kwargs):
			print "CALL WITH", args, kwargs
			from core.models import BaseObject
			key = hashlib.md5('%s;%s'%(','.join(args),','.join(kwargs.values()))).hexdigest()
			data = cache.get(key)
			print "CACHE KEY: ",key, "\nRESULT: ", data
#			if data:
#				data = BaseObject.objects.filter(id=data)
#				if data: data = data[0].direct_cast()
#				else: data = None
			if not data:
				data = f(*args, **kwargs)
				cache.set(key, data, self.time)
#				id = getattr(data, 'id', None)
#				print "SET", id
#				if id: 
#					print cache.set(key, id, self.time)
				print "REALY SET", cache.get(key)
			return data
		return wrapper

# Кэширует контекст по выбранным параметрам запроса
class cache_on_param(object):
	
	def __init__(self, prefix='', params=[], time=15*60):
		self.prefix = prefix
		self.params = params
		self.time = time
	
	def __call__(self, f):
		
		# arg[0] - object, arg[1] - request
		def wrapped_f(*args, **kwargs):
			dic = {}
			request = args[1]
			# формируем словарь значений параметров для генерации кэша
			for key in self.params:
				dic[key] = request.REQUEST.get(key, u'')
			try:
				import hashlib
			except:
				import md5 as hashlib
			
			# генерируем хэш из значений словаря параметров
			str_for_hash = u';'.join( map(lambda x: x, dic.values() ) )
			hsh = self.prefix + hashlib.md5(str_for_hash.encode('utf8')).hexdigest()
			
			from django.core.cache import cache
			# проверяем наличие в кэше
			data = cache.get(hsh)
			
			if data:
				context = data
				context['new'] = False
				return context
			else:
				context = f(*args, **kwargs)
				context['new'] = cache.add(hsh, context, self.time)
				return context
				
		return wrapped_f

def redirect_action(url):
	""" это такой декоратор, который выполняет перенаправление на определенную ссылку.
	словарь, который вернет метод, превращается в строку запроса.
        пример использования в webmail.py """
	def true_decorator(fn):
		def new(*arg):
			param = fn(*arg)
			from utils.exceptions import Http302
			raise Http302(url+"?"+"&".join([ "%s=%s"%(x,y) for x, y in param.items() ] ))
		return new
	return true_decorator
        
def text_response(fn):
	""" это такой декоратор, который не будет рендерить шаблон, не будет
        встраиваться в общую стройную систему, а просто покажет то, что вернет
        действие"""
	def new(*arg):
		res = fn(*arg)
		from utils.exceptions import EPlainTextException
		raise EPlainTextException(res)
	return new

from tsogung import settings
def mail_response(mail):
	""" это такой декоратор, который отправляет результат по почте.
	требует наличия в ответе словаря с полями subject и body.
	если в словаре ответа есть поле error -- ничего отправлять не будет,
	это для контроля ошибок, чтобы лишнего не посылать.
	после отработки возвращает управление дальше, можно отрендерить шаблон
	(см. songrequest)"""
	def true_decorator(fn):
		def new(*arg):
			res = fn(*arg)
			if not res.get('error', None): 
				subj = res.get('subject', None)
				body = res.get('body', None)
				if res and body:
					from django.core.mail import send_mail
					send_mail(subj, body, settings.DEFAULT_FROM_EMAIL, \
						  [mail,], fail_silently=True)
			return res
		return new
	return true_decorator

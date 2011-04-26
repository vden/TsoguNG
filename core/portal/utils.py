# -*- coding: utf-8 -*-

"""
	Унитилитарные функции по сборке страниц и работе с реестром и типами

	@author: Voskvitcov Denis
	@contact: vden@tsogu.ru
	@author: Vlasov Dmitry
	@contact: scailer@tsogu.ru
	@organization: TSOGU
	@status: функционирует
	@version: 1.0

	@todo 1.1: Документирование и оптимизация алгоритмов
"""

# General modules
import traceback, sys
try:
	import hashlib
except:
	import md5 as hashlib

# Django modules
from django.template import Context, RequestContext, loader as template_loader
from django.shortcuts import get_object_or_404, render_to_response
from django.http import Http404, HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.core.cache import cache

# Project modules
#from core.types import *
#from core.types.support import *
from core.registries import JSRegistry, CSSRegistry
from core.managers import FileProcessor
from tsogung.utils.exceptions import ExceptionProcessor, EPlainTextException, Http403, Http302
from core import portal
import settings
from core import REGISTRUM

def get_free_created_types():
	return [x for x in REGISTRUM if not x['create_from_workspace']]

def get_workspace_created_types():
	return [x for x in REGISTRUM if x['create_from_workspace']]

def get_actions_list():
	return [x['name'] for x in REGISTRUM['actions']]

def actions_groupe_by(field='name'):
	res = {}
	for x in REGISTRUM['actions']:
		if res.has_key(x[field]):
			res[x[field]].append(x)
		else:
			res[x[field]] = [x]
	return res

def get_action_metadata(action):
	data = actions_groupe_by().get(action)
	if not data:
		raise Exception(u'Action %s is not registred' % action)
	return data

class UnknownPortalType(Exception):
	pass

def get_type(type_name):
	try:
		return REGISTRUM['types'][type_name]['cls']
	except KeyError, E:
		raise UnknownPortalType(type_name)

# Только для обратной совместимости на время рефакторинга
TOP_CLASS_DICT = {"PageTemplate":{},
	"Poll":{}, "File":{"AudioFile":{}, "VideoFile":{}}, "Photo":{},
	"Dissertation":{}, "Link":{}, "Page":{"News":{"Event":{}}}, "Post":{}}

def direct_cast(cls):
	""" приводим тип к реальному типу потомка.
	в рекурсивной функции -- особая уличная магия определения
	верного класса для последовательно наследованных типов """

	key = "direct_cast_%s"%str(cls.id)
	data = cache.get(key)
	ocls = cls

	if data: return data

	def try_cast_by_list(d, cls):
		for c in d.keys():
			try:
				cls = eval("cls.%s"%c.lower())
				return try_cast_by_list(d[c], cls) or cls
			except:
				r = try_cast_by_list(d[c], cls)
				if r is None: continue
				return r

	cls = try_cast_by_list(TOP_CLASS_DICT, cls)
	if not cls:
		return ocls
	cache.add(key, cls, 4*60*60)
	return cls


def get_block(viewlet_dict, column, obj, req, fn, edit=False, new_type=None, data=None):
	""" Вычисляет содержимое колонки.

	column ::= {position}
	position ::= col, ":", num
	col ::= "a" | "b" | "c"
	num ::= {digit}

	Значение поля position (см. модель Viewlet):
	position_value ::= object | "$self"
	object ::= class, ":", id
	class ::= models.CLASS_DICT
	id ::= {digit}

	$self -- показывает сам объект, соответствующий текущему baseobject id.
	{a|b|c}:0 -- отключает показ соответствующей колонки.
	"""

	from core.models import BaseObject
	#raise Http404(u'asd')
	local_keys = filter(lambda x: x[0] == column and viewlet_dict[x] is not None, viewlet_dict.keys())
	if len(local_keys)>1:
		try:
			del(viewlet_dict["%s:0"%column])
			local_keys = filter(lambda x: x[0] == column, viewlet_dict.keys())
		except:
			pass

	out = u""
	if len(local_keys) == 1 and local_keys[0] == "%s:0"%column:
		return None

	local_keys.sort()

	for key in local_keys:
		if viewlet_dict[key] == "$self":
			t = obj.direct_cast()
		else:
			(cls, oid) = viewlet_dict[key].split(":")
			from core import types
#			t = getattr(types, cls).objects.get(id=oid)
			t = BaseObject.resolveID(oid)
#			t = BaseObject.objects.get(id=oid).direct_cast()
#			t = eval("%s.objects.get(id=%s)"%(cls,oid))
#		fn(t.__class__.__name__)

		# Где грязный хак, тут грязный хак?!
		req.main_object = obj
                req.session['main_object'] = obj.id

		if viewlet_dict[key] != "$self": out += t.render(req)

		# Создаем новый объект
		if new_type is not None :
                        req.session['main_object'] = None
			print REGISTRUM['types'][new_type]
			t = (viewlet_dict[key] == "$self") and REGISTRUM['types'][new_type]['cls'](parent=t, type=new_type)

		try:
			out += (viewlet_dict[key] == "$self") and (data or t.render(req)) or ''
		except EPlainTextException, E:
			raise E
		except Http302, E:
			raise E
		except Exception, E:
			out += ExceptionProcessor(req, E, sys.exc_info()).render()

	return out


def form_page(request, path_info, current_page, edit=False, new_type=False, redirect=None, data=None, columns=('a', 'b', 'c')):
	from core.models import Viewlet

	# Если нас просят перейти в другое место, переходим немедля
	if redirect: return HttpResponseRedirect(redirect)

	def get_column_block(col):
		return get_block(current_viewlet, col, main_object, request,
				 lambda x: types_list.append(x), edit, new_type, data)

	main_object = current_page
	request.session.set_test_cookie()

	# немного черной магии для того, чтобы в действиях можно было узнать,
	# откуда и как они вызваны -- сохраняем прошлый реквест
	if main_object.get_class_name() != 'Action':
		request.session['old_request'] = { 'path': request.path, 'full_path': request.get_full_path(), 'oid': main_object.id }
	try:
		request.session['old_request'].update( { 'path_info': path_info } )
	except:
		pass

	print " === FileProcessor === "
	# Файловые операции
#	fp = FileProcessor(main_object)(request)
#	request = fp and fp or request

	print " +++ FileProcessor +++ "

	current_viewlet = {}
	first_iteration = True
	while current_page != None:
		viewlets = Viewlet.objects.filter(bid=current_page)
		for v in viewlets:
			if not current_viewlet.has_key("%s:0"%v.position[0]):
				if not current_viewlet.has_key(v.position):
					if v.inherits or first_iteration:
						current_viewlet[v.position] = v.block
		current_page = current_page.parent
		first_iteration = False

	types_list = [get_object_by_url(path_info).type,]

	try:
		left_column = 'a' in columns and get_column_block("a")
		main_column = 'b' in columns and get_column_block("b")
		right_column = 'c' in columns and get_column_block("c")
	except EPlainTextException, E:
		return HttpResponse(str(E), mimetype="text/plain")
	except Exception, E:
		return ExceptionProcessor(request, E, sys.exc_info()).response()

	# Для работы с вьюлетами, два признака: режим редактирования и создания
	request.edit_object = edit
	request.new_object = new_type is None

	types_list = list(set(types_list))

	print "="*80

	return render_to_response("base.html",
			{"left_column": left_column,
			 "main_column": main_column,
			 "right_column": right_column,
			 "csses": get_css( request, request.get_full_path(), types_list),
			 "js": get_js( request, request.get_full_path(), types_list),
			 "main_object": main_object},
			context_instance = RequestContext(request))


def get_object_by_url(path_info):
	from core.models import BaseObject

	path_info = path_info.strip('/')
	hsh = "get_object_by_url_" + hashlib.md5(path_info.encode('utf8')).hexdigest()
	# проверяем наличие в кэше
	data = cache.get(hsh)
	if data:
		print "GOBU: get from cache", data.id
		return data


	head = BaseObject.objects.filter(parent__isnull=True)[0]
	current_page = head

	path = filter(lambda x: x!='', path_info.split("/"))

	for p in path:
		pages = BaseObject.objects.filter(parent=current_page)
		for i in pages:
			#TODO: оптимизировать алгоритм выбора следующей страницы,
			# иначе при паре тысяч подчиненных объектов будет ***.
			current_page = (i.slug == p) and i or None
			#	print current_page, i.slug,
			if current_page: break
		if not current_page:
			raise Http404()

	cache.add(hsh, current_page.direct_cast(), 4*60*60)
	return current_page.direct_cast()


# {{{ get files: css, js, etc

def get_files(request, path, types, timestamp_only, root, objects, css=False, fname=''):
	import os

	timestamp = 0
	base_url = path
	compiled_files = ""

	for fl in objects:
		try:
			c = eval(fl.condition)
		except Exception, E:
			c = False

		if c:
			stat = os.stat(root+fl.path)
			timestamp ^= (stat[8] + stat[6])

		if c and not timestamp_only:
			f = open(root+fl.path)
			compiled_files += "".join(f.readlines())
			f.close()

	if timestamp_only:
		return timestamp
	else:
		f = open(os.path.join(settings.MERGED_FILES, fname), "wt")
		f.write(compiled_files)
		print "save compiled %s file on disk"%fname


def get_css(request, path, local_dict=None, timestamp_only=True):
	medias = ('screen', 'print')
	r = []
	for m in medias:
		lst = CSSRegistry.objects.filter(media=m).order_by('position')
		p =  get_files(request, path, local_dict, timestamp_only, settings.CSS_ROOT, lst, css=True)
		r.append( {"type":m, "path": p} )
		fname = "%s.compiled.%s.css"%(m, p)

		import os
		is_merged_file = os.path.exists(os.path.join(settings.MERGED_FILES, fname) )

		if not is_merged_file: get_files(request, path, local_dict, False, settings.CSS_ROOT, lst, css=True, fname=fname)

	return r


def get_js(request, path, local_dict=None, timestamp_only=True):
	lst = JSRegistry.objects.all().order_by('position')
	p = get_files(request, path, local_dict, timestamp_only, settings.JS_ROOT, lst)

	fname = "compiled.%s.js"%p

	import os
	is_merged_file = os.path.exists(os.path.join(settings.MERGED_FILES, fname) )
	if not is_merged_file: get_files(request, path, local_dict, False, settings.JS_ROOT, lst, css=False, fname=fname)

	return p

# }}}


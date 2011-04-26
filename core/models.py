# -*- coding: utf-8 -*-

# Напоминание себе и потомкам: как только здесь станет больше 500 строчек --
# поставить вопрос о разбиении на более мелкие модули.

# General modules
import re
try:
	import hashlib
except ImportError:
	import md5 as hashlib

# Django modules
from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache
from django.utils.cache import get_cache_key
from django.shortcuts import get_object_or_404

# Project modules
import settings
from utils.snippets import URLify
from settings import photo_fs, file_fs
from core.managers import _BaseObjectManager
from core.portal.nodes import NodeManager
from core.middleware.threadlocals import  get_request
from core.portal.register import register_type, register_workspace
from core.portal.utils import direct_cast
from core.types.support import State, Tag, TemplateView
from core.portal.register import objectaction
from core.portal.render import render_to_portal, render_ajax, render_as_redirect


class BaseObject(models.Model):
	""" База объект, насяльника """
	title = models.CharField(u'Название', max_length=10000, blank=True)
	slug = models.SlugField(u'Slug', max_length=10000, blank=True, null=True)
	state = models.ForeignKey(State, default=1, verbose_name = u'Состояние')
	tags = models.ManyToManyField(Tag, blank=True, null=True, verbose_name = u'Метки')
	parent = models.ForeignKey("BaseObject", verbose_name = u'Предок', related_name = '%(class)s_related', null=True, blank=False)
	type = models.CharField(u'Тип', max_length=50, blank=True)

	date_modified = models.DateTimeField(u'Дата последнего изменения', auto_now=True)
	date_created = models.DateTimeField(u'Дата создания', auto_now_add=True)
	date_published = models.DateTimeField(u"Дата публикации", null=True, blank=True)

	view_template = models.ForeignKey(TemplateView, verbose_name = u'Шаблон для отображения', blank=True, null=True)
	description = models.TextField(u'Описание', blank=True, null=True)
	author = models.ForeignKey(User, verbose_name = u'Автор')
	#	object_url = models.CharField(u'Никому не видимый URL', max_length=1024, editable=False, blank=True)
	position = models.IntegerField(u'Позиция', blank=True, null=True)
	not_browse = models.BooleanField(u'Исключить из навигации', default=False)
	block = models.BooleanField(u'Заблокировать для редактирования', default=False)
	inherit_permissions = models.BooleanField(u'Наследование прав доступа', default=True)
	enable_comments = models.BooleanField(u"Разрешить комментирование", default=True)
	#todo: remove this field from db

	# Object vars
	objects = _BaseObjectManager()
	nodes = NodeManager()

	class Meta:
		unique_together = (("parent", "slug"),)
		ordering = ['title']

	# BEGIN ObjectAction's block
	@objectaction(u'Расширенная статистика')
	@render_to_portal(template='actions/extendedstat.html')
	def extended_statistic(self, request):
		path_info = request.path.split('act/extended_statistic/')[0]
		return { 'title': self.title, 'pid': path_info == '/' and "1793" or path_info }

	@objectaction(u'Удаление в корзину')
	@render_as_redirect()
	def remove(self, request):
		from utils.messages import PortalMessage
		url = self.parent.get_absolute_url()
		self._remove()
		request.portal_message.append(PortalMessage(u'Объект %s удален'%self.title).set_property(type='complete'))
		self._update_history(request)
		return url

	@objectaction(u'Удаление')
	@render_ajax(type='text')
	def destroy(self, request):
		self.delete()
		return u'Удален'

	@objectaction(u'Восстановление')
	@render_ajax(type='text')
	def restore(self, request):
		from core.portal.utils import get_object_by_url

		def rec(o, data=[]):
			ch = BaseObject.objects.filter(parent=o)
			for x in ch:
				data.append(x)
				data = rec(x, data)
			return data

		self.parent = get_object_by_url(self.config()['old_parent'])
		self.slug = self.config()['old_slug']
		self.state = State.objects.get(name='черновик')
		self.save()

		for y in rec(self):
			y.state = State.objects.get(name='черновик')
			y.save()

		del self.config()['old_slug']
		del self.config()['old_parent']

		return u'Восстановлен'

	@objectaction(u'Рейтинг')
	@render_ajax(type='text')
	def set_rate(self, request):
		try:
			r = Rating.objects.get(bid=self)
		except:
			r = Rating(bid=self)
			r.save()

		ball = request.GET.get('rating', None)
		try:
			ball = float(ball)
		except:
			return  u'Не введена оценка!'

		return r.set_vote(ball, request)

	@objectaction(u'Изменение состояния')
	@render_as_redirect()
	def state_transform(self, request):
		from core.types.support import StateTransform
		transform = get_object_or_404(StateTransform, slug=request.GET['state'])
		transform.perform(request, self)
		self._update_history(request)
		return self.get_absolute_url()

	@objectaction(u'Изменение шаблона')
	@render_as_redirect()
	def set_template(self, request):
		from core.types.support import TemplateView
		self.view_template = get_object_or_404(TemplateView, id=request.GET['template'])
		self.save()
		return self.get_absolute_url()

	@objectaction(u'Просмотр')
	@render_to_portal()
	def view(self, request):
		from django.template import RequestContext, loader as template_loader
		template = self.view_template and self.view_template.path or 'view/default/%s.html'%self.get_class_name().lower()
		context = {'object': self}
		return template_loader.get_template(template).render(RequestContext(request, context))

	@objectaction(u'Содержимое')
	@render_to_portal(template='forms/default/content.html')
	def content(self, request):
		from core.managers import FileProcessor
		FileProcessor(self)(request)
		context = {'object':self, 'portal_message':request.portal_message}
		context['process'] = request.session.has_key('process') and request.session['process'] or ''
		return context

	@objectaction(u'Конфигурация')
	@render_to_portal(template='forms/default/configlet.html')
	def configuration(self, request):
		from core.forms import BaseConfigletForm
		if request.method == 'POST':
			form = BaseConfigletForm(request.POST, instance=self)
			if form.is_valid():
				form.save()
		else:
			form = BaseConfigletForm(instance=self)
		return {'object':self, 'form':form}

	@objectaction(u'Дополнительно')
	@render_to_portal(template='forms/default/extra.html')
	def extra(self, request):
		from core.forms import extra_form_factory
		from core.portal.exceptions import Http302
		DefaultExtraPageForm = extra_form_factory(self.__class__)

		if request.method == 'POST':
			form = DefaultExtraPageForm(request.POST, instance=self)
			if form.is_valid():
				form.save()
				raise Http302(self.get_absolute_url())
		else:
			form = DefaultExtraPageForm(instance=self)

		return {'object':self, 'form':form}

	@objectaction(u'Дополнительно')
	@render_to_portal(template='forms/default/metadata.html')
	def metadata(self, request):
		return {'object':self}
	# END   ObjectAction's block

	def _remove(self):
		def rec(o, data=[]):
			ch = BaseObject.objects.filter(parent=o)
			for x in ch:
				data.append(x)
				data = rec(x, data)
			return data

		if self.block:
			pass # Message "It's block"
		else:
			self.invalidate_cache()
			self.config()['old_parent'] = self.parent.get_absolute_url()
			self.config()['old_slug'] = self.slug
			self.parent = BaseObject.objects.get(slug='trash')
			self.state = State.objects.get(name='скрытый')
			self.save()

			for y in rec(self):
				y.state = State.objects.get(name='скрытый')
				y.save()
			# Message "It's remove"

	def _drop_status(self):
		if self.state.name in [u'на редактировании', u'опубликованный', u'на главной']:
			self.state = State.objects.get(name=u'черновик')
		return self

	def _update_history(self, request):
		from datetime import datetime
		if not self.config().has_key('editing_history'):
			self.config()['editing_history'] = u'%s,%s' % (request.user.username, datetime.now().strftime('%Y.%m.%d %H:%M'))
		else:
			d = self.config()['editing_history'].split(';')
			d.append(u'%s,%s' % (request.user.username, datetime.now().strftime('%Y.%m.%d %H:%M')))
			self.config()['editing_history'] = u';'.join(d)
		self.config()['last_editor'] = request.user.username

	@classmethod
	def available_templates(cls):
		print "GET AVAILABLE TEMPLATES"
		try:
			REVERSE_TYPE = {'Page':'1', 'News':'2', 'Event':'3', 'Photo':'4', 'VideoFile':'5',\
					'AudioFile':'6', 'File':'7', 'File':'8', 'Dissertation':'9'}
			return TemplateView.objects.filter(template_type=REVERSE_TYPE[cls.__name__])
		except KeyError, E:
			return TemplateView.objects.none()

	@classmethod
	def indexing(cls):
		from xml.etree.ElementTree import ElementTree, Element
		fake_root = Element('root')
		def gchr (parents=[], res=None, depth=0):
			for x in parents:
				e = Element(x.slug, **x.__dict__)
				res.append(e)
				gchr(parents=BaseObject.objects.filter(parent=x.id), res=e, depth=depth+1)
			return res
		return ElementTree(gchr(parents=[cls.objects.get(id=1)], res=fake_root))

	def lock(self, request):
		if True: # Проверка прав доступа
			self.block = True
			self.save(force=True)
			return True
		else: return False #Хотя лучше бы raise AccessException

	def unlock(self, request):
		if True: # Проверка прав доступа
			self.block = False
			self.save(force=True)
			return True
		else: return False #Хотя лучше бы raise Exception

	def breadcrumbs(self):
		r = [ {'name':x.title, 'url':x.slug} for x in self.walktree() if x.parent ]
		for i in reversed(xrange(1, len(r)) ):
			r[i]['url'] = "/".join( [x['url'] for x in r[:i+1]] )
		return [ {'url': "/%s"%x['url'], 'name': x['name'] } for x in r ]

	def get_responsibility(self):
		from rights.models import Responsibility
		path = BaseObject.objects.look2root(self.id, False)['path']
		for id in path:
			resp = Responsibility.objects.filter(base_object__id=id)
			if resp:
				return resp

	def get_absolute_url(self):
		if self.parent_id:
			if self.id:
				return u'/%s/' % u'/'.join([x.slug for x in self.walktree() if x.parent_id])
			else:
				return u'/%s/%s/' % (u'/'.join([x.slug for x in self.parent.walktree() if x.parent_id]), self.slug)
		else:
			return u'/'

	def walktree(self):
		data = list(BaseObject.objects.raw("SELECT * FROM walk_tree(%d)" % self.id))
		data.reverse()
		return data

	def isContainable(self):
		return self.__class__.__name__ in ('Page', 'News', 'Event')

	def has_access(self, user, permission=''):
		return True

	def available_transforms(self):
		return self.state.get_available_states(self)

	def get_state(self):
		return self.state.name

	def get_child_nodes_menu(self):
		sf = 'position'
		if self.config().has_key('sort_field_'):
			sf = self.config()['sort_field_']
		st = [u'опубликованный',u'на главной']
		print "GET CHILD NODES MENU"
		return self.get_child_nodes(for_user=True, states=st, count=50, sort_field=sf, not_browse=False)

	def get_child_nodes(self, for_user=False, sort_field='position', count=None, states=[], use_config=None, tags=[], not_browse=None):
		n = BaseObject.nodes(foruser=for_user, tags=tags, states=states, sort_fields=[sort_field], parents=[self.id], not_browse=not_browse)
		if not count:
			return n.all()
		else:
			return n.limit(count)

	def get_class_name(self):
		return self.__class__.__name__

	def get_class_name_i18n(self):
		return self.__class__._meta.verbose_name

	def direct_cast(self):
		if self.type and self.id and self.get_class_name() != self.type:
			from core import types
			return getattr(types, self.type).objects.get(id=self.id)
		if self.get_class_name() == self.type:
			return self
		return direct_cast(self)

	def hidden(self):
		return self.state.name == u'скрытый'

	def twins_fix(self):
		""" Переписывает слаг таким образом, чтобы не было совпадений """
		import random
		if BaseObject.objects.filter(parent=self.parent, slug=self.slug).exclude(id=self.id):
			if self.id:
				self.slug = 'object-%s' %self.id
			else:
				self.slug = str(random.randint(100000,999999))
			return True
		return False

	def invalidate_cache(self, request=None):
		from django.utils.hashcompat import md5_constructor
		cache.delete("get_object_by_url_" + hashlib.md5(self.get_absolute_url().strip('/').encode('utf8')).hexdigest())
		cache.delete("direct_cast_%s"%str(self.id))
		cache.delete("resolveID_%s"%str(self.id))
		if '/news/university/' in self.get_absolute_url():
			cache.delete("template.cache.main_news.%s" % md5_constructor(u':'.join([])).hexdigest())
		if '/news/announcements/' in self.get_absolute_url():
			cache.delete("template.cache.main_events.%s" % md5_constructor(u':'.join([])).hexdigest())

		cache.delete("template.cache.menu.%s" % md5_constructor(u':'.join([self.get_absolute_url()])).hexdigest())
		if self.parent:
			cache.delete("template.cache.menu.%s" % md5_constructor(u':'.join([self.parent.get_absolute_url()])).hexdigest())
			if self.parent.parent:
				cache.delete("template.cache.menu.%s" % md5_constructor(u':'.join([self.parent.parent.get_absolute_url()])).hexdigest())

	def save(self, force=False, **kwargs):
		''' BO custom save '''
		print ''' === BO custom save === '''
		if not self.type:
			self.type = self.direct_cast().__class__.__name__
		if not force:
			if not self.slug:
				self.slug = URLify(self.title)
			if self.slug in ['new','edit','action','state','image','RSS']:
				self.slug += '-1'
		if not self.slug:
			from random import randint
			self.slug = 'unknown_object-%s'%randint(100000,999999)
		self.twins_fix()
		print "TWINS FIX", self.slug

		if not self.author and self.parent: self.author=self.parent.author
		self.invalidate_cache()
		print "INVALIDATE CACHE"
		print "BO SUPER SAVE BEGIN"
		if self.parent.id == self.id:
			raise Exception('Programming Error: Recursion in objects tree')
		super(BaseObject, self).save(**kwargs)
		print "BO SUPER SAVE END"

	@classmethod
	def resolveID(cls, id):
		key = "resolveID_%s"%str(id)
		data = cache.get(key)
		if data:
			return data

		try:
			obj = BaseObject.objects.get(id=id).direct_cast()
			cache.add(key, obj, 4*60*60)
		except:
			obj = None

		return obj

	def config(self):
		from utils.configdict import ConfigDict
		if not self.id: return {}
		cfg = Configlet.objects.filter(bid = self.id)
		r =  dict( [ (x.predicate, x.value) for x in cfg ] )

		obj = self.parent
		while obj:
			cfg = Configlet.objects.filter(bid=obj.id)
			for c in cfg:
				if (not r.has_key(c.predicate)) and c.inherits:
					r.update({c.predicate: c.value})
			obj = obj.parent

		return ConfigDict(initialdata=r, obj=self)

	def rating(self):
		if not self.id: return None
		try:
			r = Rating.objects.get(bid=self)
		except:
			return None
		x = r.get_rating()
		if x < 0.25: quanted_rating = 0
		else: quanted_rating = (x % 0.5 < 0.25) and (x - x%0.5) or (x + (0.5 - x%0.5))

		return quanted_rating

	def __unicode__(self):
		return u"%s(%s)"%( self.title, self.slug)[:30] + u", %s:%s"%(self.direct_cast().__class__.__name__, self.id)
	str = __unicode__


class Configlet(models.Model):
	""" Описывает набор параметров конкретного объекта """
	bid = models.ForeignKey(BaseObject, verbose_name = u'Базовый объект')
	predicate = models.CharField(u'Параметр', max_length=255)
	value = models.TextField(u'Значение', blank=True, null=True)
	inherits = models.BooleanField(u"Наследуется", default=False)


class Alias(models.Model):
	bid = models.ForeignKey(BaseObject, verbose_name = u'Базовый объект')
	url = models.CharField(u"Ссылка-алиас", max_length=10000)

	def __unicode__(self):
		return u"%s (-> %s)"%(self.url, self.bid)
	str = __unicode__

	class Meta:
		verbose_name = u'Алиас страницы'
		verbose_name_plural = u'Алиасы страниц'

class Viewlet(models.Model):
	""" Описывает положение конкретного блока на конкретной странице """
	bid = models.ForeignKey(BaseObject, verbose_name = u'Базовый объект')
	position = models.CharField(u"Положение", max_length=4)
	block = models.CharField(u"Ссылка на блок", max_length=100)
	user = models.ForeignKey(User, blank=True, null=True, verbose_name =u'Пользователь, если изменение пользовательское')
	inherits = models.BooleanField(u"Наследуется", default=True)

class Rating(models.Model):
	""" 5-ти бальная шкала оценки объектов """
	bid = models.ForeignKey(BaseObject, verbose_name = u'Базовый объект')
	rating_value = models.FloatField(u"Рейтинг", default=0, editable=False)
	rated_votes = models.PositiveIntegerField(u"Количество голосов", default=0, editable=False)
	last_vote = models.DateTimeField(u'Дата последней оценки', auto_now=True)

	def get_rating(self):
		if self.rated_votes < -5:
			return None
		else:
			return self.rating_value

	def set_vote(self, choice, request):
		if not request.session.test_cookie_worked():
			return u'Для участия в оценке включите в браузере cookies'
		key = self.get_key(request)
		request.session['%s_vote_rating'%self.id] = choice
		if key:
			if (key < 0): key = 0
			if (key > 5): key = 5
			self.rating_value = ( ( self.rating_value * self.rated_votes ) - key + choice ) / self.rated_votes
			self.save()
			print "RERATE:", key, choice
			return  u"Ваша оценка изменена. Спасибо за участие в работе портала."
		else:
			self.rating_value = ( ( self.rating_value * self.rated_votes ) + choice ) / ( self.rated_votes + 1)
			self.rated_votes += 1
			self.save()
			print "RATE:", choice
			return u'Ваша оценка принята. Спасибо за участие в работе портала.'
		return

	def get_key(self, request=None):
		request = request or get_request()
		key = request.session.get('%s_vote_rating'%self.id, None)

		try:
			return float(key)
		except:
			return None

from core.actions import *

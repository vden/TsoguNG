# -*- coding: utf-8 -*-

from django.db import models
import settings

from core import transforms
from core.transforms import EStateTransformException

from core.managers import HardCacheManager
from django.template import Context, RequestContext, loader as template_loader
from core.middleware.threadlocals import get_current_user

class State(models.Model):
	""" Состояние объекта """
	name = models.CharField(u'Название', max_length=100)
	if settings.HARDCACHE:
		objects = HardCacheManager()

	def __unicode__(self):
		return self.name
	str = __unicode__

	def get_available_states(self, object):
		""" возвращает список доступных переходов """
		from rights import has_access
		q = StateTransform.objects.filter(from_state=self)
		if not has_access(get_current_user(),'reviewing'):
			q = [x for x in q if not x.to_state.name in [u'опубликованный', u'на главной']]
		return [{'url': x.slug, 'name':x.to_state.name} for x in q]
        
        class Meta:
            app_label = "core"
        

class StateTransform(models.Model):
	slug = models.CharField(u"ID перехода", max_length=100)
	from_state = models.ForeignKey(State, blank=True, null=True, related_name="from_state_related")
	to_state = models.ForeignKey(State, blank=True, null=True, related_name="to_state_related")
	method = models.CharField(u"Метод", default="simple_transform", max_length=100)
	types = models.CharField(u"Допустимые типы", help_text=u"Список доступных типов, через запятую без пробелов. Если все -- можно написать all.", max_length=500, default="all")

	def perform(self, req, obj):
		print "PERFORM TRANSFORM"
		if not self.check_type(obj):
			return EStateTransformException("Incorrect type!")
		if not self.has_access():
			return Exception("Unauthorized!")
		m = eval("transforms.%s"%self.method)
		res = m(req, obj, self)
		obj.state = self.to_state
		obj.request = req
		obj.save(force=True)
		
		return res

	def check_type(self,obj):
		if str(self.types) != 'all':
			t = self.types.split(',')
			res = obj.get_class_name() in t
		else: res = True

		return res

	def has_access(self):
		""" например, редактор может делать новости опубликованными на главную, а
		просто менеджер -- нет """

		#TODO: сюда как-то нужно передавать заданные для перехода пермишны. где они хранятся? как? как их получить?
		#дать ответов на эти вопросы наша модель пока не может.
		return True
		
	def __unicode__(self):
		return u"%s -> %s"%(self.from_state, self.to_state)
	str = __unicode__

        class Meta:
            app_label = "core"

class Tag(models.Model):
	""" Тэг объекта  """
	name = models.CharField(u'Название', max_length=100)
	if settings.HARDCACHE:
		objects = HardCacheManager()

	def __unicode__(self):
		return self.name
	str = __unicode__

        class Meta:
            app_label = "core"

class TemplateView(models.Model):
	""" Шаблоны просмотра всего подряд """
	TYPE_CHOICE = (('1', 'Page'),
			('2', 'News'),
			('3', 'Event'),
			('4', 'Photo'),
			('5', 'Video'),
			('6', 'Audio'),
			('7', 'DocumentFile'),
			('8', 'File'),
			('9', 'Poll')	)
	name = models.CharField(u'Название', max_length=100, blank=True, null=True)
	template_type = models.CharField(u'Тип', max_length=3, choices=TYPE_CHOICE )
	path = models.CharField(u'Путь к шаблону', max_length=255)
	if settings.HARDCACHE:
		objects = HardCacheManager()

	def __unicode__(self):
		return self.name and u'%s'%self.name or u'Шаблон #%s'%self.id

	@classmethod
	def all_by_type(cls, type, TYPE_CHOICE=TYPE_CHOICE):
		return cls.objects.filter(template_type__in=[x[0] for x in TYPE_CHOICE if x[1]==type])

	def render(self, object, request=None):
		return template_loader.get_template(self.path).render(
			RequestContext(request, {'object':object}) )

	class Meta:
		app_label = "core"
		verbose_name = u'Шаблон отображения'
		verbose_name_plural = u'Шаблоны отображения'


class Category(models.Model):
	""" Категория. Метаданные, отражающие раздел для информации """
	name = models.CharField(u'Название', max_length=255)

	def __unicode__(self):
		return self.name
	str = __unicode__

	def str_id(self):
		return str(self.id)

	class Meta:            
		app_label = "core"

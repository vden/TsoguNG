# -*- coding: utf-8 -*-

from django.db import models
from core.models import BaseObject
from django.contrib.auth.models import User
from datetime import datetime as dt

class Comment(models.Model):
	base_object = models.ForeignKey(BaseObject, verbose_name=u'Объект')
	re = models.ForeignKey("Comment", verbose_name=u'RE:', null=True, blank=True)
	author = models.ForeignKey(User, verbose_name=u'Автор', related_name='comments', null=True, blank=True)

	username = models.CharField(u'ФИО', max_length=50)
	email = models.EmailField(u'email', null=True, blank=True)
	text = models.CharField(u'Текст', max_length=500)
	date_created = models.DateTimeField(u'Дата создания', auto_now_add=True)

	is_public = models.BooleanField(u'Опубликован', default=False)
	is_remove = models.BooleanField(u'Удалён', default=False)
	date_moderation = models.DateTimeField(u"Дата модерации", null=True, blank=True)
	moderator = models.ForeignKey(User, verbose_name=u'Модератор', related_name='moderated_comments', null=True, blank=True)

	def __unicode__(self):
		return u"%(bo)s -- %(author)s(%(date_created)s)"%{
			'bo': self.base_object,
			'author': self.author or self.username,
			'date_created': self.date_created }

	def get_absolute_url(self):
		return self.base_object.get_absolute_url()

	@classmethod
	def get_comments(cls, bo):
		"""
			TODO: возможно стоит сделать более сложную выборку,
			например при случае если модераторы скроют ранее опубликованный комментарий,
			который в свою очередь уже откомментирован и эти комменты опубликованы,
			есть ещё вариант: принудительно удалять все ветку, при удалении коммента
		"""
		return cls.objects.filter(base_object=bo, is_remove=False, is_public=True).order_by('date_created')

	@classmethod
	def get_comments_count(cls, bo):
		return cls.get_comments(bo).count()

	def publish(self, user):
		self.is_public = True
		self.moderator = user
		self.date_moderation = dt.now()
		self.save()
		return u"Опубликован"

	def remove(self, user):
		self.is_remove = True
		self.moderator = user
		self.date_moderation = dt.now()
		self.save()
		return u"Удалён"

	class Meta:
		verbose_name = u'Коментарий'
		verbose_name_plural = u'Коментарии'
		ordering = ('-date_created',)
		db_table = "tsogu_comments"

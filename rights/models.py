# -*- coding: utf-8 -*-

from django.db import models
from core.models import BaseObject
from django.contrib.auth.models import User, Permission, Group
from django.contrib.contenttypes.models import ContentType
import uuid
import simplejson

class Responsibility(models.Model):
	base_object = models.ForeignKey(BaseObject, verbose_name=u'Объект', unique=True)
	user = models.CharField(u'ФИО', max_length=250, default=None)
	telephone = models.CharField(u'Номер телефона', max_length=20, default=None)
	position = models.CharField(u'Должность', max_length=250, default=None)

	def __unicode__(self):
		return u'%s -- %s'%(self.position, self.user)

class DelegateRight(models.Model):
	base_object = models.ForeignKey(BaseObject, verbose_name=u'Объект')
	group = models.ForeignKey(Group, verbose_name=u'Группа')
	user = models.ForeignKey(User, verbose_name=u'Пользователь')

	class Meta:
		unique_together = ('base_object', 'group', 'user')

class ObjectPermissions(models.Model):
	base_object = models.ForeignKey(BaseObject, verbose_name=u'Объект')
	permission = models.ForeignKey(Permission, verbose_name=u'Разрешение')
	group = models.ForeignKey(Group, verbose_name=u'Группа')

	class Meta:
		unique_together = ('base_object', 'permission', 'group')

class Application(models.Model):
	uuid = models.CharField(u'UUID', max_length=36, blank=True, null=False, unique=True)
	name = models.CharField(u'Название приложения', max_length=100)
	link = models.CharField(u'Ссылка на приложение', max_length=1000)
	groups = models.CharField(u'Ссылка на группы', max_length=1000)
	public = models.BooleanField(u'Публичное', default=False)

	def __unicode__(self):
		return u'%s'%self.name

	def get_groups(self):
		try:
			import simplejson, urllib
			return simplejson.load(urllib.urlopen(self.groups))
		except:
			self.error = u'Приложение "%s" не отзывается на запрос'%self.name
			return []

	def user_groups(self, user=None):
		if hasattr(self, 'user') and not user:
			user=self.user

		res = []
		try:
			ug = [x.strip() for x in UserGroups.objects.get(application=self, user=user).groups.split(' ')]
		except:
			ug = []

		for g in self.get_groups():
			res.append({	'name':g['fields']['name'],
					'id':g['pk'],
					'choice':u'%s'%g['pk'] in ug	})
		return res

	def get_absolute_url(self):
		return u'http://www.tsogu.ru/rights/%s/%s/' % (self.public and 'go_public' or 'go', self.uuid)

	def save(self, **kwargs):
		if not self.uuid or len(self.uuid)!=36:
			self.uuid = str(uuid.uuid4()).upper()
		super(Application, self).save(**kwargs)

	class Meta:
		verbose_name = u'Приложение'
		verbose_name_plural = u'Приложения'


class UserGroups(models.Model):
	user = models.ForeignKey(User, verbose_name=u'Пользователь')
	application = models.ForeignKey(Application, verbose_name=u'Приложение')
	groups = models.TextField(u'UUID групп через пробел')

	def __unicode__(self):
		return u'%s | %s'%(self.user,self.application)

	class Meta:
		unique_together = ('user','application')
		verbose_name = u'Пользовательские группы'
		verbose_name_plural = u'Пользовательские группы'


class Token(models.Model):
	user_groups = models.ForeignKey(UserGroups, verbose_name=u'Пользовательские группы')
	token = models.CharField(u'Ключ', max_length=36, unique=True)
	date = models.DateTimeField(u'Дата регистрации', auto_now_add=True)

	def __unicode__(self):
		return u'Ключ %s'%self.token

	@classmethod
	def set(cls, user, app):
		ug = UserGroups.objects.get(user=user, application=app)
		t = Token(user_groups = ug, token = str(uuid.uuid4()).upper())
		t.save()
		return t.token

	@classmethod
	def clean(cls):
		from datetime import datetime, timedelta
		t = cls.objects.filter(date__lte=datetime.now()-timedelta(minutes=1))
		for x in t:
			x.delete()
		return u'Удалено %s устаревших ключей'%len(t)

	@classmethod
	def check(self, token):
		res = ''
		o = Token.objects.filter(token=token)
		if not o:
			res = u'Invalid key'
		else:
			ug = o[0].user_groups
			res = {}
			res['id'] 	= str(ug.user.id)
			res['username']	= ug.user.username
			res['email']	= ug.user.email
			res['groups']	= ug.groups
			res['first_name'] = ug.user.first_name
			res['last_name'] = ug.user.last_name
			res = simplejson.dumps(res)
			for x in o: x.delete()
		return res

	class Meta:
		verbose_name = u'Ключ авторизации'
		verbose_name_plural = u'Ключи авторизации'

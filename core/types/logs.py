# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User

class Log(models.Model):
	""" Системный лог """
	user = models.ForeignKey(User, verbose_name = u'Автор')
	date = models.DateTimeField(u'Дата создания', auto_now_add=True)
	title= models.TextField(u'Название')
	text = models.TextField(u'Текст')
	type = models.CharField(u'Тип', max_length=255, blank=True, null=True)

	def __unicode__(self):
		return u'%s: %s (%s / %s)'%(self.type, self.title, self.date, self.user)

	class Meta:
            app_label = "core"

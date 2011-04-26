# -*- coding: utf-8 -*-

from django.db import models

class JSRegistry(models.Model):
	path  = models.CharField(u'JS-файл', max_length=255)
	condition  = models.CharField(u'Условие', max_length=1000)
	position = models.IntegerField(u'Относительная позиция')

	def save(self, **kwargs):
		self.path = self.path.strip()
		super(JSRegistry, self).save(**kwargs)

        class Meta:
            app_label = "core"
                
class CSSRegistry(models.Model):
	path  = models.CharField(u'CSS-файл', max_length=255)
	condition  = models.CharField(u'Условие', max_length=1000)
	position = models.IntegerField(u'Относительная позиция')
	media  = models.CharField(u'Media', max_length=20)

	def save(self, **kwargs):
		self.path = self.path.strip()
		super(CSSRegistry, self).save(**kwargs)

        class Meta:
            app_label = "core"

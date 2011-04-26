# -*- coding: utf-8 -*-
from core.models import BaseObject, register_type, file_fs
from django.db import models
import settings
from django import forms
from django.contrib.admin import widgets as admin_widgets
from core.fields import TinyMCEWidget
from core.portal.register import objectaction
from core.portal.render import render_to_portal
from core.portal.exceptions import Http302

from utils.snippets import URLify
from core.help import register_help, ContextHelpNote

class File(BaseObject):
	""" Файлы. Просто файлы, документы, аудио, видео. В идеале -- на каждый тип свой просмотр """
	path = models.FileField(u'Путь к файлу', storage=file_fs, upload_to = '%Y/%m_%d')

	@objectaction(u'Правка')
	@render_to_portal(template='forms/default/file.html')
	def edit(self, request):
		return self._edit(request)

	@classmethod
	@render_to_portal(template='forms/default/file.html')
	def _create(cls, request, parent):
		obj = cls(parent=parent, author=request.user, type=cls.__name__)
		return obj._edit(request)

	def _edit(self, request):
		if request.method == 'POST':
			form = DefaultGeneralFileForm(request.POST, request.FILES, instance=self)
			if form.is_valid():
				form.save()
				raise Http302(self.get_absolute_url())
		else:
			form = DefaultGeneralFileForm(instance=self)
		return {'object':self, 'form':form}

	def save(self, **kwargs):
		import os
		if not self.title: self.title = self.path and os.path.splitext(self.path.name)[0] or u'Без названия'
		self.path.name = URLify(self.path.name, strong=False)
		super(File, self).save(**kwargs)

	class Meta:
		verbose_name = u"Файл"
		verbose_name_plural = u"Файлы"
		app_label = "core"

class DefaultGeneralFileForm(forms.ModelForm):
	class Meta:
		model = File
		fields = ('title','description','path', 'tags')
		widgets = {
				'path':admin_widgets.AdminFileWidget(attrs={}),
				'description':forms.Textarea(attrs={'cols':'80','rows':'5'}),
				'tags':admin_widgets.FilteredSelectMultiple(u'метки', 0)
			}

	class Media:
		js = ('/media/js/admin_jsi18n.js',)





register_type(File)

register_help(
ContextHelpNote(
	u'File',
	u'Файл',
	u'Объект на основе файла произвольного типа. Загруженный файл можно скачать.'
))

register_help(
ContextHelpNote(
	u'path',
	u'Путь к файлу',
	u'Указывается путь к файлу на Вашем компьютере, который будет загружен на портал.'
))

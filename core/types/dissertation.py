# -*- coding: utf-8 -*-
from core.models import BaseObject, register_type, register_workspace
from django.db import models
import settings
from django import forms
from django.contrib.admin import widgets as admin_widgets
from core.fields import CalendarDateField, TinyMCEWidget
from core.portal.register import objectaction
from core.portal.render import render_to_portal
from core.portal.exceptions import Http302

class Dissertation(BaseObject):
	""" Объявление о защите диссертаций """
	subject = models.TextField(u'Тема диссертации')
	date_defend = models.DateTimeField(u'Дата защиты')
	dissertant = models.CharField(u'Ф.И.О. соискателя', max_length=500)
	speciality = models.CharField(u'Специальность', max_length = 500)
	council = models.TextField(u'Диссертационный совет')
	autoref = models.CharField(u'URL автореферата', max_length = 5000, blank=True)

	@objectaction(u'Правка')
	@render_to_portal(template='forms/default/base_edit.html')
	def edit(self, request):
		return self._edit(request)

	@classmethod
	@render_to_portal(template='forms/default/base_edit.html')
	def _create(cls, request, parent):
		obj = cls(parent=parent, author=request.user, type=cls.__name__)
		return obj._edit(request)

	def _edit(self, request):
		if request.method == 'POST':
			form = DefaultGeneralDisserForm(request.POST, instance=self._drop_status())
			if form.is_valid():
				form.save()
				self._update_history(request)
				raise Http302(self.get_absolute_url())
		else:
			form = DefaultGeneralDisserForm(instance=self)
		return {'object':self, 'form':form}

	class Meta:
		verbose_name = u"Диссертация"
		verbose_name_plural = u"Диссертации"
		app_label = "core"

	def save(self, **kwargs):
		self.description = u""
		super(Dissertation, self).save(**kwargs)
		if self.title != self.dissertant:
			self.title = self.dissertant
			self.save()

class DefaultGeneralDisserForm(forms.ModelForm):
	subject = Dissertation._meta.get_field("subject").formfield(label=u'Тема диссертации')
	dissertant = Dissertation._meta.get_field("dissertant").formfield(label=u'Ф.И.О. соискателя')
	speciality = Dissertation._meta.get_field("speciality").formfield(label=u'Специальность')
	autoref = Dissertation._meta.get_field("autoref").formfield(label=u'Ссылка на файл автореферата')
	council = Dissertation._meta.get_field("council").formfield(widget=forms.Textarea(attrs={'cols':'80','rows':'3'}))
	date_defend = CalendarDateField(label=u'Дата защиты', required=True)

	class Meta:
		model = Dissertation
		fields = ( 'dissertant','subject', 'date_defend', 'speciality', 'council', 'autoref','tags')
		widgets = {
				'tags':admin_widgets.FilteredSelectMultiple(u'метки', 0)
			}

	class Media:
		js = ('/media/js/admin_jsi18n.js',)

register_type(Dissertation, base=None)
register_workspace(Dissertation, u"Объявление о защите диссертации", u"/resources/dissers/", u"Объявление о защите диссертации с датой защиты и файлом автореферата.")

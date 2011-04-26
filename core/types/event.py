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
from core.types.news import News

class Event(News):
	""" Событие. Начинается, кончается, по-своему отображается. Как будто бы новость --
	    есть категория, но плюс даты конца-начала и т.п. """
	date_start = models.DateTimeField(u'Дата начала', auto_now=False)
	date_end = models.DateTimeField(u'Дата окончания', auto_now=False)
	place = models.CharField(u'Место', max_length=1000, blank=True, null=True)
	contact_name = models.CharField(u'Контактное имя', max_length=1000, blank=True, null=True)
	contact_email = models.CharField(u'Контактная электронная почта', max_length=1000, blank=True, null=True)
	contact_phone = models.CharField(u'Контактный телефон', max_length=1000, blank=True, null=True)
	#TODO: добавить остальные поля: участники, руководители, место и т.д.

	@objectaction(u'Просмотр')
	@render_to_portal()
	def view(self, request):
		from django.template import RequestContext, loader as template_loader
		template = self.view_template and self.view_template.path or 'view/default/%s.html'%self.get_class_name().lower()
		context = {'object': self}
		return template_loader.get_template(template).render(RequestContext(request, context))

	@objectaction(u'Правка')
	@render_to_portal(template='forms/default/base_edit.html')
	def edit(self, request):
		return self._edit(request)

	def print_form(self):
		pass #заглушка

	def _edit(self, request):
		if request.method == 'POST':
			form = DefaultGeneralEventForm(request.POST, instance=self._drop_status())
			if form.is_valid():
				form.save()
				self._update_history(request)
				raise Http302(self.get_absolute_url())
		else:
			form = DefaultGeneralEventForm(instance=self)

		return {'object':self, 'form':form}

	class Meta:
		verbose_name = u"Событие"
		verbose_name_plural = u"События"
		app_label = "core"

class DefaultGeneralEventForm(forms.ModelForm):
	date_start = CalendarDateField(label=u'Дата начала')
	date_end = CalendarDateField(label=u'Дата завершения')

	def __init__(self, *args, **kwrds):
		super(DefaultGeneralEventForm, self).__init__(*args, **kwrds)
		self.fields['text'].widget.is_new = not bool(kwrds['instance'].id)

	class Meta:
		model = Event
		fields = ('title','description','text','date_start','date_end',
			'place','contact_name','contact_email','contact_phone', 'tags')
		widgets = {
				'text':TinyMCEWidget(),
				'description':forms.Textarea(attrs={'cols':'80','rows':'5'}),
				'tags':admin_widgets.FilteredSelectMultiple(u'метки', 0)
			}

	class Media:
		js = ('/media/js/admin_jsi18n.js',)


register_type(Event, base=News)
register_workspace(Event, u"Событие", u"/news/events/", u'Анонсы событий отображаются в календаре по соответствующим датам и в блоке «Анонсы» с описанием.')

# -*- coding: utf-8 -*-

from django import forms
from core.fields import CalendarDateField
from django.contrib.admin import widgets as admin_widgets
from core import models
from datetime import datetime


def extra_form_factory(type):
	class BaseExtraForm(forms.ModelForm):
		time_choices = [('None',u'не задано')] + [('%s'%x,'%2d:00'%x) for x in xrange(0,25)]

		slug = forms.SlugField(label=u'Адрес', required=False)
		date_published = CalendarDateField(label=u'Дата публикации', required=False)
		time = forms.ChoiceField(label = u'Время публикации', required=False, choices=time_choices)
		view_template = forms.ModelChoiceField(label=u"Шаблон",queryset=type.available_templates(),empty_label="(стандартный шаблон)",required=False)

		def __init__(self, *args, **kw):
			try:
				kw['initial'] = {'time':str(kw['instance'].date_published.hour)}
			except:
				kw['initial'] = {'time':'None'}
			super(BaseExtraForm, self).__init__(*args, **kw)

		def save(self):
			s = super(BaseExtraForm, self).save()
			if self['time'].data != 'None':
				d = s.date_published
				s.date_published = datetime(d.year, d.month, d.day, int(self['time'].data))
				s.save()

		class Meta:
			model = type
			fields = ('slug','view_template','not_browse','block','date_published')
	return BaseExtraForm


class BaseConfigletForm(forms.ModelForm):
	bid = models.Configlet._meta.get_field("bid").formfield(widget=forms.HiddenInput())
	value = forms.CharField(label = u'Значение')
	remove = forms.CharField(label = u'Удалить')

	class Meta:
		model = models.Configlet
		fields = ('predicate','value','bid')

	def is_valid(self):
		if self['predicate'].data:
			return True
		return False

	def save(self):
		conf = models.Configlet.objects.filter(bid = self['bid'].data,
				predicate = self['predicate'].data)

		if conf:
			conf = conf[0]
			if str(self['remove'].data) == 'True':
				conf.delete()
				return True
		else:
			conf = models.Configlet()

		conf.predicate = self['predicate'].data
		conf.value = self['value'].data
		conf.bid = models.BaseObject.objects.get(id=self['bid'].data)
		conf.save()

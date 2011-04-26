# -*- coding: utf-8 -*-
from django import forms
from django.forms.util import flatatt
from django.utils.encoding import smart_unicode
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.simplejson.encoder import JSONEncoder


class DateTimeWidget(forms.DateTimeInput):
	class Media:
		js = ('js/jquery-1.3.2.min.js','js/jquery-ui-1.7.2.custom.min.js','js/calendar_loc.js')

class TinyMCEWidget(forms.Textarea):
	def __init__(self, *args, **kwargs):
		self.is_new = True
		if not kwargs.has_key('attrs'):
			kwargs['attrs'] = {}
		kwargs['attrs'].update({'cols':'80','rows':'30'})
		super(TinyMCEWidget, self).__init__(*args, **kwargs)

	def render(self, name, value, attrs=None):
		if value is None: 
			value = ''

		if self.is_new:
			from settings.tinymce import new_MCE as MCE
		else:
			from settings.tinymce import MCE

		value = smart_unicode(value)
		final_attrs = self.build_attrs(attrs, name=name)

		MCE['elements'] = "id_%s" % name
		mce_json = JSONEncoder().encode(MCE)
		return mark_safe(u'<textarea%s>%s</textarea> <script type="text/javascript">\
			tinyMCE.init(%s)</script>' % (flatatt(final_attrs), escape(value), mce_json))

	class Media:
		js = ('js/tiny_mce/tiny_mce.js',)


class CalendarDateField(forms.DateField):
	def __init__(self, *args, **kwargs):
		super(CalendarDateField, self).__init__(*args, **kwargs)
		self.input_formats = ('%d.%m.%y','%d.%m.%Y')
		self.widget=DateTimeWidget(attrs={'class':'datepick'},format='%d.%m.%Y')

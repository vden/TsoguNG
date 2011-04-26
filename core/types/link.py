# -*- coding: utf-8 -*-
from core.models import BaseObject, register_type
from django.db import models
from django import forms
from core.portal.register import objectaction
from core.portal.render import render_to_portal
from core.portal.exceptions import Http302

from core.help import register_help, ContextHelpNote

class Link(BaseObject):
	TYPE_CHOICE = (('1', u'Локальная ссылка (внутри портала, любой тип)'),
		       ('2', u'Ссылка на страницу'),
		       ('3', u'Ссылка на изображение'),
		       ('4', u'Ссылка на видеофайл'),
		       ('5', u'Ссылка на аудиофайл')
		       )
	url = models.CharField(u"Адрес ссылки", max_length=1000)
	link_type = models.CharField(u"Тип ссылки", max_length=2, default='2', choices=TYPE_CHOICE)

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
			form = DefaultGeneralLinkForm(request.POST, instance=self)
			if form.is_valid():
				form.save()
				raise Http302(self.get_absolute_url())
		else:
			form = DefaultGeneralLinkForm(instance=self)
		return {'object':self, 'form':form}

	def get_link_absolute_url(self):
#		if int(self.link_type) == 1:
		return self.url

	class Meta:
		verbose_name = u"Ссылка"
		verbose_name_plural = u"Ссылки"
		app_label = "core"

class DefaultGeneralLinkForm(forms.ModelForm):
	class Meta:
		model = Link
		fields = ('title','description','url', 'link_type')
		widgets = {
				'description':forms.Textarea(attrs={'cols':'80','rows':'5'}),
			}



register_type(Link)


register_help(
ContextHelpNote(
	u'Link_url',
	u'Ссылка',
	u'Адрес ссылки.')
)

register_help(
ContextHelpNote(
	u'Link',
	u'Ссылка',
	u'Ссылка на внешний или внутренний ресурс.')
)

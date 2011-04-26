# -*- coding: utf-8 -*-
from core.models import BaseObject, register_type
from django.db import models
from django import forms
from django.contrib.admin import widgets as admin_widgets
from core.fields import TinyMCEWidget
from core.portal.register import objectaction
from core.portal.render import render_to_portal
from core.portal.exceptions import Http302

class PostTag(models.Model):
	name = models.CharField(u'Название', max_length=100)
	def __unicode__(self):
		return self.name
	str = __unicode__

	class Meta:
		app_label = "core"


class Post(BaseObject):
	""" Произвольная страница портала, основной заполняющий элемент """
	text = models.TextField(u'Текст', null=True, blank=True)
	posttags = models.ManyToManyField(PostTag, verbose_name=u'Теги', null=True, blank=True)

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
			form = DefaultGeneralPostForm(request.POST, instance=self)
			if form.is_valid():
				form.save()
				raise Http302(self.get_absolute_url())
		else:
			form = DefaultGeneralPostForm(instance=self)
		return {'object':self, 'form':form}


	class Meta:
		verbose_name = u"Пост"
		verbose_name_plural = u"Посты"
		app_label = 'core'

class DefaultGeneralPostForm(forms.ModelForm):
	class Meta:
		model = Post
		fields = ('title','description','text', 'posttags')
		widgets = {
				'text':TinyMCEWidget(),
				'description':forms.Textarea(attrs={'cols':'80','rows':'5'}),
				'posttags':admin_widgets.FilteredSelectMultiple(u'метки', 0)
			}

	class Media:
		js = ('/media/js/admin_jsi18n.js',)



register_type(Post)

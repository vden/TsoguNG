# -*- coding: utf-8 -*-
from core.models import BaseObject, register_type, register_workspace
from core.types.support import Category
from django.db import models
import settings
from django import forms
from django.contrib.admin import widgets as admin_widgets
from core.portal.register import objectaction
from core.portal.render import render_to_portal
from core.fields import TinyMCEWidget
from core.portal.exceptions import Http302
from django.shortcuts import render_to_response

from core.types.page import Page
from core.help import register_help, ContextHelpNote

class News(Page):
	""" Та же страница, но возможно с другой версткой и указанной категорией """
	category = models.ForeignKey(Category, verbose_name = u'Категогия новости', null=True, blank=True)
	edit_template = None #?
	template_default_conf = dict(tags='on', text='on', photo='block', signature='on', links='on', files='on', comments='on')

	@objectaction(u'Правка')
	@render_to_portal(template='forms/default/base_edit.html')
	def edit(self, request):
		return self._edit(request)

	def _edt(self, request):
		if request.method == 'POST':
			form = DefaultGeneralNewsForm(request.POST, instance=self._drop_status())
			if form.is_valid():
				form.save()
				self._update_history(request)
				raise Http302(self.get_absolute_url())
		else:
			form = DefaultGeneralNewsForm(instance=self)
		return {'object':self, 'form':form}

	@objectaction(u'Печатная форма')
	def print_form(self, request):
		context = {'object': self}
		return render_to_response("print.html", context)

	def get_nested_links(self):
		return BaseObject.nodes().parents(self).types('Link').states(u'опубликованный').all()

	class Meta:
		verbose_name = u"Новость"
		verbose_name_plural = u"Новости"
		app_label = "core"

class DefaultGeneralNewsForm(forms.ModelForm):
	title = forms.CharField(label = u'Заголовок', required=True)

	def __init__(self, *args, **kwrds):
		super(DefaultGeneralNewsForm, self).__init__(*args, **kwrds)
		self.fields['text'].widget.is_new = not bool(kwrds['instance'].id)

	class Meta:
		model = News
		fields = ('title','description','text','tags')
		widgets = {
				'text':TinyMCEWidget(),
				'description':forms.Textarea(attrs={'cols':'80','rows':'5'}),
				'tags':admin_widgets.FilteredSelectMultiple(u'метки', 0)
			}

	class Media:
		js = ('/media/js/admin_jsi18n.js',)



register_type(News, base=Page)
register_workspace(News,  u"Новость", u"/news/university/", u'Новости отображаются на главной странице или на страницах институтов, в зависимости от состояния и присвоенных меток.')


register_help(
ContextHelpNote(
	u'News',
	u'Новость',
	u'Страница специально выделенная для хранения новостных сообщений (новостью являтся уже произошедшее событие). Все новостные сообщения должны создаваться из рабочей зоны пользователя, иначе они не будут попадать в автоматически собираемые летны новостей. Важно помнить, что агрегация новостей в ленты подразделений происходит по меткам (тегам).',
	u'http://www.tsogu.ru/video-spravka/razmeshchenie-novostej/')
)

register_help(
ContextHelpNote(
	u'News_tags',
	u'Метки',
	u'Метки небходимы для агрегации новостей в новостные ленты подразделений')
)

register_help(
ContextHelpNote(
	u'category',
	u'Категория',
	u'Категория новости в действующей версии сайта используется только в качестве дополнительного текствового описания к новости. Агрегация новостей осуществляется не по категории, как это было ранее, а то меткам (тегам).')
)

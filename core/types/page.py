# -*- coding: utf-8 -*-
from core.models import BaseObject, register_type, register_workspace, photo_fs
from django.db import models
import settings
from core.portal.register import objectaction
from core.portal.render import render_to_portal, render_ajax, render_as_redirect
from django import forms
from django.contrib.admin import widgets as admin_widgets
from core.fields import TinyMCEWidget

from core.help import register_help, ContextHelpNote
from core.portal.exceptions import Http302

class Page(BaseObject):
	""" Произвольная страница портала, основной заполняющий элемент """
	text = models.TextField(u'Текст', null=True, blank=True)
	template_default_conf = dict(description='on', text='on', photo='block', files='on')

	def _edit(self, request):
		if request.method == 'POST':
			form = DefaultGeneralPageForm(request.POST, instance=self._drop_status())
			if form.is_valid():
				form.save()
				self._update_history(request)
				raise Http302(self.get_absolute_url())
		else:
			form = DefaultGeneralPageForm(instance=self)
		return {'object':self, 'form':form}

	@objectaction(u'Правка')
	@render_to_portal(template='forms/default/base_edit.html')
	def edit(self, request):
		return self._edit(request)

	@objectaction(u'Настройка шаблона')
	@render_to_portal(template='forms/default/template_conf.html')
	def template_conf(self, request):
		import simplejson

		keys = ('tags', 'description', 'text', 'photo', 'signature', 'content', 'links', 'files', 'comments')
		values = dict(
				photo=('block', 'albom', 'gallery'),
				content=('with_date', 'without_date', 'with_image'))

		if request.method == 'POST':
			config = dict([(key,value)  for key, value in request.POST.items()
				if key in keys and value in values.get(key, ('on',))])
			self.config()['template_conf'] = simplejson.dumps(config)
			raise Http302(self.get_absolute_url())
		else:
			if 'default' in request.GET:
				if 'template_conf' in self.config():
					del self.config()['template_conf']
				raise Http302(self.get_absolute_url())
			else:
				try:
					config = simplejson.loads(self.config()['template_conf'])
				except:
					config = self.template_default_conf

		return {'config': config, 'object': self}

	@objectaction(u'Просмотр')
	@render_to_portal()
	def view(self, request):
		import simplejson
		from django.template import RequestContext, loader as template_loader

		try:
			template_config = simplejson.loads(self.config()['template_conf'])
		except:
			template_config = self.template_default_conf

		template = self.view_template and self.view_template.path or 'view/default/meta.html'
		context = {'object': self, 'template_config': template_config}
		return template_loader.get_template(template).render(RequestContext(request, context))

	@objectaction(u'Добавить', check_access=False)
	def insert(self, request):
		from rights import check_permission, has_access
		from django.contrib.auth.models import Permission
		from django.contrib.contenttypes.models import ContentType

		from core import types
		cls = getattr(types, request.GET['type'])
		content_type = ContentType.objects.get_for_model(cls)
		permission = Permission.objects.get(codename='insert', content_type=content_type)
		if not has_access(request.user, permission, self):
			raise Http403

		if not self.isContainable:
			raise Exception(u'В данном объекте не возможно создавать другие объекты')

		return cls._create(request=request, parent=self)

	@classmethod
	@render_to_portal(template='forms/default/base_edit.html')
	def _create(cls, request, parent):
		obj = cls(parent=parent, author=request.user, type=cls.__name__)
		return obj._edit(request)

	def get_images(self):
		res = []
		for x in self.get_child_nodes():
			if x.get_class_name() == 'Photo' \
			       and not x.not_browse \
			       and not x.hidden():
				res.append(x)
		return res

	def get_front_image(self):
		i = self.get_images()
		return len(i) > 0 and i[0] or False

	def thumbnail_cropped(self, size):
		img = self.get_front_image()
		if img:
			from utils.snippets import thumbnail_cropped
			return thumbnail_cropped(photo_fs, img.image, size)

	def thumbnail_resized(self, size):
		img = self.get_front_image()
		if img:
			from utils.snippets import thumbnail_cropped
			return thumbnail_resized(photo_fs, img.image, size)

	def get_news(self):
		from core.types import News
		return [x.direct_cast() for x in News.objects.filter(tags__in=self.tags.all(), state__name__in = (u"на главной",
				u"опубликованный")).exclude(id=self.id).order_by('-date_published')[:10]]

	class Meta:
		verbose_name = u"Страница"
		verbose_name_plural = u"Страницы"
		app_label = 'core'

class DefaultGeneralPageForm(forms.ModelForm):
	title = forms.CharField(label = u'Заголовок', required=True)

	def __init__(self, *args, **kwrds):
		super(DefaultGeneralPageForm, self).__init__(*args, **kwrds)
		self.fields['text'].widget.is_new = not bool(kwrds['instance'].id)

	class Meta:
		model = Page
		fields = ('title','description','text', 'tags')
		widgets = {
				'text':TinyMCEWidget(),
				'description':forms.Textarea(attrs={'cols':'80','rows':'5'}),
				'tags':admin_widgets.FilteredSelectMultiple(u'метки', 0)
			}

	class Media:
		js = ('/media/js/admin_jsi18n.js',)


register_type(Page)
register_workspace(Page, u"Объявление", u"/news/announcements/", u'Короткие текстовые объявления. Отображаются в блоке «Объявления».')


register_help(
ContextHelpNote(
	u'Page',
	u'Страница',
	u'Страница - основной объект портала. Страница одновременно является и странице, и папкой, в которой могут содержаться объекты. Таким образом весь портал представляет собой дерево (иерархию) страниц. Вложенные в страницу фото, будут отображаться в блоке фото страницы (если выбран шаблон - по умолчанию). Помните, что размещая объемные ресурсы на часто посещаяемых страницах, Вы мешаете работе пользователей и тратите их время и интернет трафик, и что размещая множество изображений на странице, Вы делаете ее нечитаемой.')
)

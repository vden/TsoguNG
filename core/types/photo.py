# -*- coding: utf-8 -*-
from core.models import BaseObject, register_type, photo_fs
from django.db import models
import settings
from django import forms
from django.contrib.admin import widgets as admin_widgets
from core.portal.register import objectaction
from core.portal.render import render_to_portal
from core.portal.exceptions import Http302


from utils.snippets import handle_thumb, URLify
from core.help import register_help, ContextHelpNote

class Photo(BaseObject):
	""" Фотография 9 на 12 """
	image = models.ImageField(u'Фото', storage=photo_fs, upload_to='%Y/%m_%d')
	thumbnail = models.ImageField(storage=photo_fs, upload_to='thumbs/%Y/%m_%d', editable=False, blank = True)

	@objectaction(u'Правка')
	@render_to_portal(template='forms/default/file.html')
	def edit(self, request):
		return self._edit(request)

	@classmethod
	@render_to_portal(template='forms/default/file.html')
	def _create(cls, request, parent):
		print "CREATE", cls
		obj = cls(parent=parent, author=request.user, type=cls.__name__)
		return obj._edit(request)

	def _edit(self, request):
		if request.method == 'POST':
			form = DefaultGeneralPhotoForm(request.POST, request.FILES, instance=self)
			if form.is_valid():
				form.save()
				raise Http302(self.get_absolute_url())
		else:
			form = DefaultGeneralPhotoForm(instance=self)
		return {'object':self, 'form':form}


	def save(self, **kwargs):
		""" Photo custom save """
		if not self.title: self.title = str(self.image).split('/')[-1].split('.')[0] or u'Без названия'
		self.image.name = URLify(self.image.name, strong=False)
#		self.image = handle_thumb(fs, self.image, self.image, 700, 525)
		super(Photo, self).save(**kwargs)
		self.thumbnail = handle_thumb(photo_fs, self.image, self.thumbnail, 160, 500) # width, height
		super(Photo, self).save(**kwargs)
#		if not self.thumbnail: 
#			self.thumbnail = handle_thumb(photo_fs, self.image, self.thumbnail, 160, 500) # width, height
#			self.save()

	def url(self):
		return self.image.url

	def thumb_url(self):
		return self.thumbnail.url

	def thumbnail_cropped(self, size):
		from utils.snippets import thumbnail_cropped
		return thumbnail_cropped(photo_fs, self.image, size)

	def thumbnail_resized(self, size):
		from utils.snippets import thumbnail_resized
		return thumbnail_resized(photo_fs, self.image, size)

	class Meta:
		verbose_name = u"Изображение"
		verbose_name_plural = u"Изображения"
		app_label = "core"

class DefaultGeneralPhotoForm(forms.ModelForm):
	class Meta:
		model = Photo
		fields = ('title','description','image', 'tags')
		widgets = {
				'description':forms.Textarea(attrs={'cols':'80','rows':'5'}),
				'tags':admin_widgets.FilteredSelectMultiple(u'метки', 0),
				'image':admin_widgets.AdminFileWidget(attrs={})
			}

	class Media:
		js = ('/media/js/admin_jsi18n.js',)




register_type(Photo)

register_help(  
ContextHelpNote(
	u'Photo',
	u'Фото',
	u'Объект на основе изображения. В качестве изображения желательно использовать растровые изображения популярных форматов (png, jpg, gif), так как другие форматы изображений могут не распознаваться браузерами пользователей. Желательно, чтобы размещаемые изображения не превышали 0,5 Мб. Недопустимо размещение изображений больше 1 Мб или в несжатых форматах (bmp и т.п.) на часто посещаемых страницах. Помните, что размещая объемные ресурсы на часто посещаяемых страницах, Вы мешаете работе пользователей и тратите их время и интернет трафик, и что размещая множество изображений на странице, Вы делаете ее нечитаемой.')
)

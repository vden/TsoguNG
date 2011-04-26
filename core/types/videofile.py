# -*- coding: utf-8 -*-
from core.models import BaseObject, register_type, file_fs
from django.db import models
import settings
from django import forms
from django.contrib.admin import widgets as admin_widgets
from core.portal.register import objectaction
from core.portal.render import render_to_portal
from utils.snippets import URLify
from core.types.file import File
from django.db.models.signals import post_save
from core.help import register_help, ContextHelpNote
from core.portal.exceptions import Http302

def handle_video_info(sender, **kwargs):
	obj = kwargs['instance']
	if not obj.preview:
		from subprocess import call, Popen
		from os import path
		loc = file_fs.location
		thumb = "%s.png"% path.splitext(obj.path.name)[0]

		retcode = call("""ffmpeg -v -1 -y -i "%s" -vframes 1 -ss 00:00:12 -an -vcodec png -f rawvideo "%s" """%\
				       (obj.path.path, path.join(loc, thumb)), shell=True)
		if retcode == 0: 
			obj.preview = thumb
		else:
			obj.preview = "%simg/question_y.png"%settings.MEDIA_URL

		input_file = obj.path.path
		if input_file.lower()[-4:] != '.flv':
			flv_file = "%s.flv"%path.splitext(obj.path.name)[0]
			output_file = path.join(loc, flv_file)
			# асинхронный вызов перекодировщика
			# TODO: написать хитрого демона и обращаться к нему с запросом на постановку в очередь
			# на перекодирование. а тот в свою очередь может дергать джангу ответом о конце перекодирования...
			ffmpeg_pid = Popen(["sh", "%s/core/recode_video.sh"%settings.working_dir, input_file, output_file]).pid
			obj.path = flv_file

		obj.save()
			
class VideoFile(File):
	preview = models.ImageField(u"Изображение для предпросмотра", storage=file_fs,  upload_to='%Y/%m_%d', blank=True)

	@objectaction(u'Правка')
	@render_to_portal(template='forms/default/file.html')
	def edit(self, request):
		if request.method == 'POST':
			form = DefaultGeneralVideoFileForm(request.POST, request.FILES, instance=self)
			if form.is_valid():
				form.save()
				raise Http302(self.get_absolute_url())
		else:
			form = DefaultGeneralVideoFileForm(instance=self)
		return {'object':self, 'form':form}

	def is_ready(self):
		""" проверяет, есть ли в реальности файл, который обозначен в поле.
		обычно, если такого файла нет — значит он еще не перекодирован до конца
		надо бы как-то сделать этот метод побыстрее"""
		if not self.preview:
			return False
		import os
		try:
			os.stat(self.path.path)
		except Exception:
			return False
		return True

	def save(self, **kwargs):
		super(VideoFile, self).save(**kwargs)

	def thumbnail_cropped(self, size):
		from utils.snippets import thumbnail_cropped
		return thumbnail_cropped(file_fs, self.preview, size)

	def thumbnail_resized(self, size):
		from utils.snippets import thumbnail_resized
		return thumbnail_resized(file_fs, self.preview, size)

	class Meta:
		verbose_name = u"Видеофайл"
		verbose_name_plural = u"Видеофайлы"
		app_label = "core"

class DefaultGeneralVideoFileForm(forms.ModelForm):
	class Meta:
		model = VideoFile
		fields = ('title','description','path', 'preview', 'tags')
		widgets = {
				'preview':admin_widgets.AdminFileWidget(attrs={}),
				'path':admin_widgets.AdminFileWidget(attrs={}),
				'description':forms.Textarea(attrs={'cols':'80','rows':'5'}),
				'tags':admin_widgets.FilteredSelectMultiple(u'метки', 0)
			}

	class Media:
		js = ('/media/js/admin_jsi18n.js',)



post_save.connect(handle_video_info, sender=VideoFile)
register_type(VideoFile, base=File)


register_help(  
ContextHelpNote(
	u'VideoFile',
	u'Видеофайл',
	u'Объект на основе видеороика. Позволяет просматривать запись с портала и скачивать ее к себе на компьютер. Комментирование и оценка видеофайла доступна по умолчанию. Все опубликованные видеоролики попадают в раздел телевидения ТюмГНГУ.')
)

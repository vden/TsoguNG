# -*- coding: utf-8 -*-
from django.db.models.signals import post_save
from core.models import BaseObject, register_type
from django.db import models

from core.types.file import File
from core.help import register_help, ContextHelpNote

def handle_audio_info(sender, **kwargs):
	obj = kwargs['instance']
	if obj.length == 0:
		print "POST_SAVE"
		from utils.MP3Info import MP3Info
		try:
			mp3info = MP3Info(open(obj.path.path, "rb"))
			obj.length = mp3info.mpeg.total_time
			obj.save()
		except Exception, E:
			print "POST_SAVE AudioFile exception", str(E)

class AudioFile(File):
	length = models.IntegerField(u"Длительность трека", blank=True, default=0)

	def save(self, **kwargs):
		super(AudioFile, self).save(**kwargs)

	def mediainfo(self):
		mi = {}		
		mi['length'] = "%02d:%02d"%(self.length//60, self.length%60)

		return mi
	class Meta:
		verbose_name = u"Аудиофайл"
		verbose_name_plural = u"Аудиофайлы"
		app_label = "core"

post_save.connect(handle_audio_info, sender=AudioFile)
register_type(AudioFile, base=File)


register_help( 
ContextHelpNote(
	u'AudioFile',
	u'Аудиофайл',
	u'Объект на основе файла формата mp3. Позволяет прослушивать запись с портала и скачивать ее к себе на компьютер. Комментирование и оценка аудиофайла доступно по умолчанию.')
#	u'http://www.tsogu.ru/video-spravka/razmeshchenie-novostej/')
)


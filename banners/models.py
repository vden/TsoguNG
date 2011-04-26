# -*- coding: utf-8 -*-

from django.db import models
import settings
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_save, pre_delete
from django.core.cache import cache

banner_fs = FileSystemStorage(location=settings.BANNERS_ROOT)

class BannerGroup(models.Model):
	name = models.CharField(u"Название группы", max_length=200)
	count = models.IntegerField(u"Количество баннеров")
	
	def __unicode__(self):
		return self.name
	str = __unicode__

class Banner(models.Model):
	title = models.CharField(u"Название баннера", max_length = 200, null = True, blank=True)

	effective_date = models.DateTimeField(u"Дата вступления в силу")
	expire_date = models.DateTimeField(u"Дата истечения срока действия", null=True, blank=True)

	groups = models.ManyToManyField(BannerGroup, verbose_name=u"Группы баннера")

	link = models.CharField(u"Ссылка", max_length = 5000)
	new_window = models.BooleanField(u"Открывать в новом окне", default=True)
	image = models.FileField(u"Файл баннера", storage = banner_fs, upload_to="%Y/%m_%d")

	resize = models.BooleanField(u"Масштабировать баннер по ширине колонки", default=False)

	def __unicode__(self):
		return u"banner %s, %s(%s), %s-%s"%(self.image, self.id, self.title, self.effective_date, self.expire_date)
	str = __unicode__

	def url(self):
		return "%s%s"%(settings.BANNERS_URL, self.image)

	def is_flash(self):
		return str(self.image)[-4:].lower() == '.swf'

def invalidate_banners_cache(sender, **kw):
	for k in BannerGroup.objects.all():
		print "CALL SIGNAL:", "bannerscachett_%s"%k.name
		cache.delete("bannerscachett_%s"%k.name)
post_save.connect(invalidate_banners_cache, sender=Banner)
pre_delete.connect(invalidate_banners_cache, sender=Banner)
post_save.connect(invalidate_banners_cache, sender=BannerGroup)
pre_delete.connect(invalidate_banners_cache, sender=BannerGroup)

class TextBanner(models.Model):
	title = models.CharField(u"Название баннера", max_length = 200, null = False, blank=False)

	effective_date = models.DateTimeField(u"Дата вступления в силу")
	expire_date = models.DateTimeField(u"Дата истечения срока действия", null=True, blank=True)

	groups = models.ManyToManyField(BannerGroup, verbose_name=u"Группы баннера")
	
	link = models.CharField(u"Ссылка", max_length = 5000)
	new_window = models.BooleanField(u"Открывать в новом окне", default=True)

	color = models.CharField(u"Цвет баннера", max_length = 20, null=False, default=u"#6389B5")

	def __unicode__(self):
		return u"text banner  %s(%s), %s-%s"%(self.id, self.title, self.effective_date, self.expire_date)
	str = __unicode__

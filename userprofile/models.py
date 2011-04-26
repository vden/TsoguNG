# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
import settings

from core.models import photo_fs

class Profile(models.Model):
	user   = models.OneToOneField(User, verbose_name=u'Пользователь', related_name="user_profile", primary_key=True)
	avatar = models.ImageField(u'Аватар', storage=photo_fs, upload_to='avatar/%Y_%m/', blank=True, null=True)

	middle_name = models.CharField(u'Отчество', max_length=250, blank=True, null=True)
	subscription = models.CharField(u'Подпись', max_length=250, blank=True, null=True)
	is_email_confirmed = models.BooleanField(u'Подтверждён ли email', default=False)

	student_id = models.PositiveIntegerField(u'Студент', blank=True, null=True)

	class Meta:
		verbose_name = u'Профиль пользователя'
		verbose_name_plural = u'Профили пользователей'
		ordering = ('user__username',)

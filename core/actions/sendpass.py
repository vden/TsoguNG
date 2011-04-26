# -*- coding:utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.core.mail import send_mail
import settings
from core.portal.register import portalaction
from core.portal.render import render_to_portal

class SendpassForm(forms.Form):
	login = forms.CharField(label = u'Логин')
	email = forms.CharField(label = u'Эл.почта')

	message = u''

	def is_valid(self):
		if super(SendpassForm,self).is_valid():
			return bool(self.get_user())
		else:
			False

	def get_user(self):
		try:
			return User.objects.get(username=self['login'].data, email=self['email'].data)
		except:
			self.message = u'Пользователя с такими учетными данными не существует'
			return None

@portalaction(verbose_name=u'Востановление пароля', condition='isAnonymous')
@render_to_portal(template='actions/sendpass.html')
def sendpass(request):
	if request.method=="POST":
		form = SendpassForm(request.POST)
		if form.is_valid():
			user = form.get_user()
			passwd = User.objects.make_random_password()
			user.set_password(passwd)
			user.save()
			send_mail(u'Востановление пароля', u'Доброго времени суток.\nВаш пароль на портале www.tsogu.ru сброшен. Новые учетные данные:\nЛогин: %s\nПароль: %s\n\n---\nС уважением,\nвебмастер www.tsogu.ru,\nwebmaster@tsogu.ru' % (user.username, passwd), settings.DEFAULT_FROM_EMAIL,[user.email,],fail_silently=False)
			form.message = u'Пароль отправлен'
	else:
		form = SendpassForm()

	return {'form':form}

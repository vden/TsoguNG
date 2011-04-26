# -*- coding: utf-8 -*-

import re
from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.utils.translation import ugettext as _
from django.template import loader
from core.portal.exceptions import Http302
from django.contrib.auth import authenticate, login
from core.portal.register import portalaction
from core.portal.render import render_to_portal, render_as_redirect

from captcha.fields import CaptchaField

RE_USERNAME = getattr(settings, 'ACCOUNT_RE_USERNAME', re.compile(r'[a-z0-9][_a-z0-9]*[a-z0-9]$', re.I))
USERNAME_MIN_LENGTH = getattr(settings, 'ACCOUNT_USERNAME_MIN_LENGTH', 3)
USERNAME_MAX_LENGTH = getattr(settings, 'ACCOUNT_USERNAME_MAX_LENGTH', 20)

PASSWORD_MIN_LENGTH = getattr(settings, 'ACCOUNT_PASSWORD_MIN_LENGTH', 5)
PASSWORD_MAX_LENGTH = getattr(settings, 'ACCOUNT_PASSWORD_MAX_LENGTH', 15)

class UsernameField(forms.CharField):
	def __init__(self, *args, **kwargs):
		super(UsernameField, self).__init__(*args, **kwargs)
		self.help_text = u'При создании доступны следующие символы a-z, 0-9 и символ подчёркивания. Длина имени пользователя должна быть от %(min)s до %(max)s символов.' % {'min': USERNAME_MIN_LENGTH, 'max': USERNAME_MAX_LENGTH}

	def clean(self, value):
		super(UsernameField, self).clean(value)

		if len(value) < USERNAME_MIN_LENGTH:
			raise forms.ValidationError(u'Длина имени пользователя меньше %(min)d символов' % {'min': USERNAME_MIN_LENGTH})
		if len(value) > USERNAME_MAX_LENGTH:
			raise forms.ValidationError(u'Длина имени пользователя больше %(max)d символов' % {'max': USERNAME_MAX_LENGTH})
		if not RE_USERNAME.match(value):
			raise forms.ValidationError(u'Имя пользователя содержит запрещенные символы')

		try:
			User.objects.get(username__exact=value)
		except User.DoesNotExist:
			return value
		else:
			raise forms.ValidationError(u'Данное имя пользователя уже используется.')


class PasswordField(forms.CharField):

	def __init__(self, *args, **kwargs):
		super(PasswordField, self).__init__(*args, **kwargs)
		self.widget = forms.PasswordInput()

	def clean(self, value):
		super(PasswordField, self).clean(value)
		if len(value) < PASSWORD_MIN_LENGTH:
			raise forms.ValidationError(_(u'Длина пароля меньше %(min)d символов') % {'min': PASSWORD_MIN_LENGTH})
		if len(value) > PASSWORD_MAX_LENGTH:
			raise forms.ValidationError(_(u'Длина пароля больше %(max)d символов') % {'max': PASSWORD_MAX_LENGTH})
		return value


class RegistrationForm(forms.ModelForm):
	username = UsernameField(label=u'Имя пользователя')
	email = forms.EmailField(label=u'Адрес электронной почты')
	password = PasswordField(label=u'Пароль', help_text=u'Длина пароля должна быть от %(min)s до %(max)s символов' %{'min':PASSWORD_MIN_LENGTH, 'max':PASSWORD_MAX_LENGTH})
	password_dup = PasswordField(label=u'Пароль (подтверждение)')
	captcha = CaptchaField(label=u'Защита от автоматических регистраций', help_text=u'Введите текст с картинки. Если Вы не можете прочесть текст — обновите страницу.')

	class Meta:
		model = User
		exclude = ('is_superuser','is_staff', 'last_login', 'first_name', 'last_name',
					'date_joined','is_active','groups','user_permissions', 'password')

	def __init__(self, *args, **kwargs):
		super(RegistrationForm, self).__init__(*args, **kwargs)

	
	def clean_email(self):
		try:
			User.objects.get(email__exact=self.cleaned_data['email'])
		except User.DoesNotExist:
			return self.cleaned_data['email']
		except KeyError:
			pass
		else:
			raise forms.ValidationError(u'Данный email уже используется другим пользователем')

	
	def clean(self):
		pwd1 = self.cleaned_data.get('password')
		pwd2 = self.cleaned_data.get('password_dup')
		if pwd1 and pwd2:
			if pwd1 != pwd2:
				self._errors['password_dup'] = [u'Введённые пароли не совпадают']
		return self.cleaned_data


	def save(self):
		username = self.cleaned_data['username']
		email = self.cleaned_data['email']
		password = self.cleaned_data['password']
		user = User.objects.create_user(username, email, password=password)
		user.save()
		return user


@portalaction(verbose_name=u'Регистрация', category='user', condition='isAnonymous')
@render_to_portal(template='actions/registration.html')
def registration(request):
	if 'POST' == request.method:
		form = RegistrationForm(request.POST)
	else:
		form = RegistrationForm()
	if form.is_valid():
		form.save()
		user = authenticate(username=request.POST['username'], password=request.POST['password'])
		login(request, user)
		raise Http302('/portal/workspace/?portal_message=account_complete')
	return {'form': form}

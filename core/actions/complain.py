# -*- coding: utf-8 -*-

from core.portal.register import portalaction
from core.portal.render import render_to_portal, render_as_redirect, render_ajax
from django.template import RequestContext, loader as template_loader
from django import forms
import settings

class ComplainForm(forms.Form):
	username = forms.CharField(label=u"ФИО", max_length=50)
	email = forms.EmailField()
	text = forms.CharField(widget=forms.Textarea)
	object = forms.IntegerField(widget=forms.HiddenInput())
	url = forms.CharField(widget=forms.HiddenInput())

	def send(self, user):
		from django.conf import settings
		from django.core.mail import send_mail

		cleaned_data = self.cleaned_data
		object = cleaned_data.get('object', u'не определён')
		url = cleaned_data.get('url', u'не определён')
		text = cleaned_data.get('text', u'не определён')
		subject = u"Жалоба с портала www.tsogu.ru"
		user_str = u" ".join([unicode(user), getattr(user, 'first_name', ''), getattr(user, 'last_name', ''), 'email: ', getattr(user, 'email', '')])
		body = u'''Данное письмо было отправлено вам с портала http://www.tsogu.ru.\nuser: %s\nobject: %s\nurl: http://www.tsogu.ru%s\n\nСобственно текст письма:\n%s'''%(user_str, object, url, text)
		send_mail(subject, body, cleaned_data['email'], settings.EDITOR_EMAILS, fail_silently=False)

	def clean_object(self):
		from django.core.exceptions import ObjectDoesNotExist
		from core.models import BaseObject
		data = self.cleaned_data['object']
		if data:
			try:
				data = BaseObject.objects.get(id=data)
			except ObjectDoesNotExist:
				raise forms.ValidationError(u"Объекта с указанным id не существует.")
		return data

@portalaction(verbose_name=u'Отправить письмо редактору портала')
@render_ajax(type='html')
def complain(request):
	from django.forms.util import ErrorList
	user = request.user
	if request.method == 'GET':
		initial = {}
		if user.is_authenticated():
			try:
				profile = request.user.get_profile()
			except:
				profile = None
			initial['username'] = ' '.join([name for name in user.last_name, user.first_name, getattr(profile, 'middle_name', '') if name])
			if not initial['username']: initial['username'] = request.user.username
			initial['email'] = request.user.email
		initial['object'] = request.GET.get('object')
		initial['url'] = request.GET.get('url')
		form = ComplainForm(initial=initial, auto_id=None)
	else:
		form = ComplainForm(request.POST, auto_id=None)
		if form.is_valid():
			try:
				form.send(request.user)
				return u"Ваше сообщение отправлено на email редактору портала."
			except Exception, e:
				form._errors.setdefault('__all__', ErrorList(e))
	context = {'form': form }
	return template_loader.get_template("actions/complain.html").render(
			RequestContext(request, context))

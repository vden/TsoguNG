# -*- coding: utf-8 -*-

from django.http import HttpResponse
from userprofile.models import Profile
from django.contrib.auth.models import User
import settings
from uuid import uuid5, UUID
from core.portal.render import render_to_portal, render_ajax
from django.template import RequestContext, loader as template_loader
from core.portal.exceptions import Http302

@render_to_portal(template='profile/index.html')
def index(request):
	context = {}
	user = request.user
	if not user.is_authenticated():
		raise Http302('/login/')
	try:
		context['profile'] = user.get_profile()
	except:
		context['profile'] = None
	context['user'] = user
	return context

@render_ajax(type="html", template='profile/view.html')
def update(request):
	context = {}
	user = request.user
	if not user.is_authenticated():
		raise Http302('/login/')
	try:
		context['profile'] = user.get_profile()
	except:
		context['profile'] = None
	return context

@render_ajax(type="html")
def edit(request):
	from forms import ProfileForm
	context = {}
	user = request.user
	if not user.is_authenticated():
		raise Http302('/login/')
	try:
		profile = user.get_profile()
	except:
		profile = None
	if request.method == 'POST':
		form = ProfileForm(request.POST)
		if form.is_valid():
			data = form.cleaned_data
			user.last_name = data['last_name']
			user.first_name = data['first_name']

			drop_email = user.email != data['email']

			user.email = data['email']
			user.save()
			if data['middle_name'] or data['subscription']:
				if profile:
					profile.middle_name = data['middle_name']
					profile.subscription = data['subscription']
				else:
					profile = Profile(user=user,
							middle_name=data['middle_name'],
							subscription = data['subscription'])

				if drop_email:
					profile.is_email_confirmed = False

				profile.save()
			return u'Данные успешно сохранены'
		context['form'] = form
	else:
		data = {'last_name':user.last_name,
				'first_name': user.first_name,
				'email':user.email}
		if profile:
			data['middle_name'] = profile.middle_name
			data['subscription'] = profile.subscription
		context['form'] = ProfileForm(initial=data)
	context['profile'] = profile
	return template_loader.get_template("profile/edit.html").render(
			RequestContext(request, context))

@render_ajax()
def send_email_confirm(request):
	from django.core.mail import send_mail
	from uuid import uuid5, UUID
	import settings

	if not request.user.is_authenticated():
		raise Http302('/login/')

	code = uuid5(UUID(settings.UUID_NAMESPACE_FOR_EMAIL_CONFIRM), str(request.user.email))
	subj = u'[www.tsogu.ru] Подтверждение email'
	body = u'Доброго времени суток.\n\nПользователь %s отправил запрос на подтверждение электронной почты. Для подтверждения электронной почты на сайте ТюмГНГУ пройдите по ссылке:\nhttp://www.tsogu.ru/userprofile/email_confirm/%s/%s/\nЕсли данное письмо попало к Вам по ошибке - удалите его.\n\n---\nС уважением,\nАдминистрация портала www.tsogu.ru,\nwebmaster@tsogu.ru' % (request.user.username, request.user.id, code)

	try:
		send_mail(subj, body, settings.DEFAULT_FROM_EMAIL, [request.user.email], fail_silently=False)
		return u'Пароль подтверждения отправлен на электронную почту'
	except:
		return u'Произошел сбой при отправке почты. Повторите попытку позже или сообщите вебмастеру о сбое.'

def student_status_confirm(request):
	import urllib
	import simplejson as json
	from hashlib import md5

	import settings

	user = request.user
	if not user.is_authenticated():
		raise Http302('/login/')
	try:
		userprofile = user.get_profile()
	except:
		userprofile = Profile(user=user)
	login = request.POST.get('login', '')
	password = md5(request.POST.get('password', '').encode('utf-8')).hexdigest()
	params = "login=%s&password=%s"%(login.encode('utf-8'), password)
	result = urllib.urlopen(settings.EDUCON_URL, params).read() or u"Произошла досадная ошибка, попробуйте позже."
	try:
		userprofile.student_id = int(result)
		userprofile.save()
		return HttpResponse(u"Статус студента подтверждён, обновите профиль.", mimetype="text/plain")
	except:
		return HttpResponse(content=result, mimetype="text/plain", status=500)

def get_student_info(student_id):
	import urllib2, base64
	import simplejson as json

	import settings

	params = "field=group"
	request = urllib2.Request('%sstudents/student/%d/?%s'%(settings.API_TSOGU, student_id, params))
	base64string = base64.encodestring('%s:%s' % (settings.API_TSOGU_USERNAME, settings.API_TSOGU_PASSWORD))[:-1]
	authheader =  "Basic %s" % base64string
	request.add_header("Authorization", authheader)
	data = json.loads(urllib2.urlopen(request).read())
	return data


def email_confirm(request, user_id, code):
	user = User.objects.get(id=user_id)
	true_code = uuid5(UUID(settings.UUID_NAMESPACE_FOR_EMAIL_CONFIRM), str(user.email))
	if str(true_code) == str(code):
		try:
			profile = user.get_profile()
		except:
			profile = Profile(user=user)
		profile.is_email_confirmed = True
		profile.save()
		return HttpResponse(u'Ваш email подтвержден')
	else:
		return HttpResponse(u'Код подтверждения не верен')

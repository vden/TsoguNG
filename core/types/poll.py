# -*- coding: utf-8 -*-
from core.models import BaseObject, register_type, register_workspace
from django.db import models
import settings
from django import forms
from core.portal.register import objectaction
from core.portal.render import render_to_portal
from core.portal.exceptions import Http302

from core.fields import CalendarDateField
from django.contrib.admin import widgets as admin_widgets
from core.middleware.threadlocals import  get_request, set_cookie

class PollVote(models.Model):
	""" Голос """
	poll = models.ForeignKey("Poll", verbose_name=u'Голосование')
	choice = models.ForeignKey("PollChoice", verbose_name=u'Вариант ответа')
	key = models.CharField(u'Идентификатор', max_length=100)
	
	class Meta:
		app_label = "core"

class PollChoice(models.Model):
	""" Вариант ответа """
	poll = models.ForeignKey("Poll", verbose_name=u'Голосование')
	choice = models.CharField(max_length=1000, verbose_name=u'Вариант ответа')

        def count(self):
		return PollVote.objects.filter(choice=self).count()

	def get_results(self):
		c = self.count()
		ca = self.poll.count() or 1
		return {'count':c, 'percent':100*float(c)/float(ca), 'percent_verbose':u'%2.2f %%'%(100*float(c)/float(ca))}

	def __unicode__(self):
		return u'%s (%s)'%(self.choice, self.poll)
	
	class Meta:
		app_label = "core"

class Poll(BaseObject):
	""" Голосовалка """
	expire_date = models.DateTimeField(u"Дата истечения срока действия", null=True, blank=True)

	@objectaction(u'Правка')
	@render_to_portal(template='forms/default/poll.html')
	def edit(self, request):
		return self._edit(request)

	@classmethod
	@render_to_portal(template='forms/default/poll.html')
	def _create(cls, request, parent):
		obj = cls(parent=parent, author=request.user, type=cls.__name__)
		return obj._edit(request)

	def _edit(self, request):
		if request.method == 'POST':
			form = DefaultGeneralPollForm(request.POST, instance=self)
			if form.is_valid():
				form.save()
				raise Http302(self.get_absolute_url()+'act/edit/')
		else:
			form = DefaultGeneralPollForm(instance=self)
		return {'object':self, 'form':form}

	def set_vote(self, choice, request):
		if not request.session.test_cookie_worked():
			return u'Для участия в опросе включите в браузере cookies'
		elif not self.access(request):
			return u'Вы уже оставили свой голос в этом опросе'
		else:
			key = request.COOKIES.has_key(settings.SESSION_COOKIE_NAME) and request.COOKIES[settings.SESSION_COOKIE_NAME] or u'unknown'
			PollVote(poll=self, choice=choice, key=key).save()
			return u'Ваш голос принят. Спасибо за участие в опросе.'

	def access(self, request=None):
		request = request or get_request()
		if not request.session.test_cookie_worked(): return False
		key = request.COOKIES.has_key(settings.SESSION_COOKIE_NAME) and request.COOKIES[settings.SESSION_COOKIE_NAME] or u'unknown'
		if key in [x.key for x in PollVote.objects.filter(poll=self)]:
			return False
		else:
			return True
	
	@classmethod
	def active(cls):
		from django.db.models import Q
		from datetime import datetime
		now = datetime.now()
		return cls.objects.filter( Q(expire_date__isnull = True) | Q(expire_date__gt = now) ) 

	def is_active(self):
		from datetime import datetime
		now = datetime.now()
		return self.expire_date > now 

	def choices(self):
		return PollChoice.objects.filter(poll=self).order_by('id')

	def count(self):
		return PollVote.objects.filter(poll=self).count()

	class Meta:
		verbose_name = u"Голосование"
		verbose_name_plural = u"Голосования"
		app_label = "core"

from django.forms.models import modelform_factory, modelformset_factory, inlineformset_factory
DefaultGeneralPollFormInline = inlineformset_factory(Poll, PollChoice, extra=5, max_num=25)


class DefaultGeneralPollMainForm(forms.ModelForm):
	title = Poll._meta.get_field("title").formfield(label=u'Вопрос')
	expire_date = CalendarDateField(label=u'Дата истечения срока', required=False)

	class Meta:
		model = Poll
		fields = ['title','description', 'tags','expire_date']
		widgets = {
				'description':forms.Textarea(attrs={'cols':'80','rows':'3'}),
				'tags':admin_widgets.FilteredSelectMultiple(u'метки', 0)
			}

	class Media:
		js = ('/media/js/admin_jsi18n.js',)



class DefaultGeneralPollForm:
	form = DefaultGeneralPollMainForm
	formset = DefaultGeneralPollFormInline

	def __init__(self, data=None, files=None, instance=None):
		self.instance = instance
		self.data = data
		self.files = files
		self.iform = self.form(data, files, instance=instance)
		self.iformset = self.formset(data, files, instance=instance)
		print "FS", [x for x in self.iformset.forms[0]], self.iformset.forms[0].fields

	def is_valid(self):
		return self.iform.is_valid() and self.iformset.is_valid()

	def save(self):
		self.iform.save()
		self.iformset.save()

	def __unicode__(self):
		from django.utils.safestring import mark_safe
		return mark_safe(u'%s %s'%(self.iform, self.iformset))


register_type(Poll)
register_workspace(Poll, u"Голосование", u"/news/polls/items/",  u'Голосование по какому-либо вопросу. Если указать метки, то будет отображаться на соответствующих им страницах сайта. Последнее опубликованное голосование отображается в блоке «Опрос».')

# -*- coding: utf-8 -*-

from utils.exceptions.e4xx import *
from utils.exceptions.e3xx import *
from django.http import HttpResponse, HttpResponseRedirect 
import traceback

class EPlainTextException(Exception):
	pass

class ExceptionProcessor:
	
	def __init__(self, request, exception, sys_exc_info):
		self.request = request
		self.exception = exception
		self.sei = sys_exc_info

	def render(self):
		try:
			if not hasattr(self.exception, 'render'):
				return self.e500()
			else: 
				return self.exception.render(self.request)
		except:
			raise self.exception

	def e500(self):
		import settings
		from django.core.mail import mail_admins
		(exc_type, exc_info, tb) = self.sei
		response = u'<div class="traceback">'
		response += u'<div><h3>Произошла ошибка</h3></div>'
		response += u'<div class="exc">%s: %s</div>' % (exc_type.__name__, exc_info)
		title = u'%s: %s' % (exc_type.__name__, exc_info)
		response += u'<div class="message">В процессе выполнения операции произошла ошибка. Информация о данном инциденте отправлена разработчиками. Приносим свои извинения.<br/><a href="http://www.tsogu.ru">На главную</a></div>'
		response += u'<div style="marging-top:5px;">Трассировка:</div>'
		for tb in traceback.extract_tb(tb):
			response += u'<div class="traceline"><b>Файл:</b>&nbsp;&nbsp;<i>%s</i><br/><b>Функция:</b> &nbsp;&nbsp;<i>%s</i><br/><b>Строка %s:</b> &nbsp;&nbsp;<i>%s</i></div>' % (tb[0], tb[2], tb[1], tb[3])
		response += u'</div>'
		if getattr(settings, 'SEND_EXCEPTIONS', False):
			pass #mail_admins('%s: %s' % (exc_type.__name__, exc_info), response)
		if getattr(settings, 'LOG_EXCEPTIONS', False):
			try:
				from core.types.logs import Log
				Log(user=self.request.user, type=u'Ошибка', title=title, text=response).save()
			except:
				pass #mail_admins(u'Ошибка логирования', u'Произошла ошибка логирования. Проверте наличие таблиц в базе.')
		return response

	def response(self):
		if not hasattr(self.exception, 'response'): raise self.exception
		else: return self.exception.response(self.request)

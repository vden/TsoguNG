# -*- coding: utf-8 -*-

class Http403(Exception):
	def __init__(self, message=u'Недостаточно прав доступа для получения объекта.'):
		self.code=403
		self.message=message

	def __str__(self):
		return self.message

class Http404(Exception):
	def __init__(self, message=u'Запрашиваемый объект не найден.'):
		self.code=404
		self.message=message

	def __str__(self):
		return self.message

class Http302(Exception):
	def __init__(self, url='/'):
		self.code=302
		self.url=url

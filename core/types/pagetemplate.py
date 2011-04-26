# -*- coding: utf-8 -*-
from core.models import BaseObject, register_type
from django.db import models
import settings

import core.custom as custom
from django.template import Context, RequestContext, loader as template_loader
from core.portal.register import objectaction
from core.portal.render import render_to_portal, render_ajax, render_as_redirect

class PageTemplate(BaseObject):
	"""
	Произвольный шаблон. Календарик, баннерокрутилка или
	ERP-система, встроенная в правую колонку сайта.

	Из модуля custom вызывается метод с именем шаблона без .html,
	метод должен вернуть контекст для шаблона (любого типа,
	лишь бы шаблон с ним смог разобраться).

	Переменная в конфигурации может выглядеть так:
	CUSTOM_TEMPLATES = "custom/"
	"""
	template = models.CharField(u'Путь к шаблону', max_length=255)

	def render(self, request=None):
		tpl = "%s%s"%(settings.CUSTOM_TEMPLATES, str(self.template))
		method = eval("custom.%s"%self.slug)

		context = method(self, request)
		param = {'object':self,}
		param.update(context)
		return template_loader.get_template(tpl).render(
			RequestContext(request, param)) 

	@objectaction(u'Просмотр')
	@render_to_portal()
	def view(self, request):
		return self.render(request)

	class Meta:
		app_label = "core"
register_type(PageTemplate, user=False)

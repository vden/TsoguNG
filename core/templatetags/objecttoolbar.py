# -*- coding: utf-8 -*-
from django import template
from rights import has_access
register = template.Library()

def objecttoolbar(context, obj):
	request = context['request']
	context['action'] = request.action
	if request.action == 'insert':
		context['new'] = True
		context['has_access'] = request.user.is_authenticated and has_access(request.user, 'insert', location=obj.parent.direct_cast())
	else:
		context['has_access'] = request.user.is_authenticated and has_access(request.user, 'edit', location=obj.direct_cast())
		context['tabs'] = [(u'view',u'Просмотр'),(u'content',u'Содeржимое'),(u'edit',u'Правка'),\
					(u'extra',u'Дополнительно'),(u'metadata',u'Метаданные')]
		if obj.type in ('News', 'Page') and not obj.view_template:
			context['tabs'].append((u'template_conf', u'Настройка&nbsp;шаблона'))
		if request.user.is_superuser or u'Owner' in [x.name for x in request.user.groups.all()]:
			context['tabs'].append((u'configuration',u'Конфигурация'))
	return context
register.inclusion_tag('objecttoolbar.html', takes_context=True)(objecttoolbar)

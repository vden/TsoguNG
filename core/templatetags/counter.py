# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import SafeUnicode
register = template.Library()

tpl = """<div style="height: 31px;float:right;padding: 0.5em 0"><a href="%(url)sact/extended_statistic/"><img width="88" height="32" border="0" src=" http://app.tsogu.ru/counter/stat_drawing.cgi?page=%(path)s"></a>&nbsp;</div>"""

@register.tag
def counter(parser, token):
    return CounterNode()

class CounterNode(template.Node):
	def render(self, context):
		path = context['request'].META['PATH_INFO']
		# немного черной магии для того, чтобы откидывать страницы статистики и т.д.
		path = path.split("act/extended_statistic/")[0]
		if path == "/": path = "1793"

		try:
			res = tpl % {'path':path, 'url':context['request'].main_object.get_absolute_url()}
		except:
			res = ''

		return res


from django import template
from core import REGISTRUM
register = template.Library()

@register.tag
def actions(parser, token):
	try:
		tag, category, q, var = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError, "Actions templatetag error"
	return ActionNode(category, var)

class ActionNode(template.Node):
	def __init__(self, category, var):
		self.category = eval(category)
		self.var = var

	def render(self, context):
		request = context['request']

		isAnonymous = not request.user.is_authenticated()
		isAuthenticated = request.user.is_authenticated()
		isSuperuser = request.user.is_superuser
		isStaff = request.user.is_staff
		groups = [x.name for x in request.user.groups.all()]

		context[self.var] = [val for key, val in REGISTRUM['actions'].items()\
					if val['category'] == self.category and eval(val['condition'])]

		return ''

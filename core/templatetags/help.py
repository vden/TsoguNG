from django import template
from core.help import HELP_NOTES
register = template.Library()

@register.tag
def help(parser, token):
	try:
		tag, key = token.split_contents()
	except ValueError:
		raise template.TemplateSyntaxError, "Help system templatetag error"

	return HelpNode(key)

class HelpNode(template.Node):
	def __init__(self, key):
		self.key = eval(key)

	def render(self, context):
		obj = None
		try:
			if self.key == 'model':
				try:
					k = str(context['form'].Meta.model.__name__)
					obj = HELP_NOTES[k]
				except KeyError:
					 print "MODEL HELP NOT FOUND: ",context['form'].Meta.model.__name__

			if self.key == 'field':
				try:
					k = '%s_%s'%(context['form'].Meta.model.__name__,context['field'].name)
					if k not in HELP_NOTES.keys():
						k = '%s'%context['field'].name
					obj = HELP_NOTES[k]
				except KeyError:
					print "FIELD HELP NOT FOUND: ",context['field'].name

			if self.key not in ('field','modelfield','model'):
				try:
					obj = HELP_NOTES[self.key]
				except:
					print "HELP NOT FOUND: ",self.key
			print "OBJECT HELP", obj
		except:
			pass
		return obj and obj.render() or u''

# -*- coding:utf-8 -*-
from django import template
from core.views import get_object_by_url
from django.utils.safestring import SafeUnicode
register = template.Library()

@register.tag
def objects_by_tag(parser, token):
    try:
        tag_name, parent, tag, dummy, var = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly three arguments" % token.contents.split()[0]

 #   if not (tag[0] == tag[-1] and tag[0] in ('"', "'")):
  #      raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name

    return ObjectsByTagNode(parent, tag, var)

class ObjectsByTagNode(template.Node):
    def __init__(self, parent, tag, var):
        self.parent = template.Variable(parent)
        self.tag = template.Variable(tag)
        self.var = var

    def render(self, context):
        try:
            parent_obj = self.parent.resolve(context)
            if type(parent_obj)==SafeUnicode: 
                parent_obj = get_object_by_url(parent_obj)
            tag = self.tag.resolve(context)

            context[self.var] = parent_obj.get_child_nodes(for_user=True, states=[u'опубликованный',u'на главной'], \
                                                               tags=[tag,], sort_field="-date_published")
        except template.VariableDoesNotExist:
            pass

        return ''

        

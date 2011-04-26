from django import template

register = template.Library()

@register.tag
def range(parser, token):
    try:
        tag_name, start, end, step, dummy, var = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly four arguments" % token.contents.split()[0]

    return RangeNode(start, end, step, var)

class RangeNode(template.Node):
    def __init__(self, start, end, step, var):
        self.start = template.Variable(start)
        self.end = template.Variable(end)
        self.step = template.Variable(step)
        self.var = var

    def render(self, context):
        try:
            start = int(self.start.resolve(context))
            end = int(self.end.resolve(context))
            step = float(self.step.resolve(context))

            context[self.var] = [x * step for x in xrange(start + 1, end / step + 1)]
        except Exception, E:
            context[self.var] = []

        return ''

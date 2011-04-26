from django import template
from core.views import get_object_by_url
from django.utils.safestring import SafeUnicode
register = template.Library()
from core.models import BaseObject

@register.tag
def nodes(parser, token):
    try:
        param_array = token.split_contents()
        param_array = param_array[1:]
        var = param_array[-1:][0]
        param_array = param_array[:-2]
        # if len(param_array) < 2 or len(param_array)%2: 
        #     if not isinstance(param_array[0], list): 
        #         print param_array[0]
        #         raise ValueError()
        #     else:
        #         param_array = reduce(lambda x,y:x+y, param_array[0])
        #         print "CONVERTED", param_array
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires even number of arguments or array" % token.contents.split()[0]

    return ObjectNodesNode(param_array, var)

class ObjectNodesNode(template.Node):
    def __init__(self, param_array, var):
        self.param_array = []
    
        for i in param_array:
            self.param_array.append(template.Variable(i))
    
        self.var = var

    def render(self, context):
        if len(self.param_array)==1:
            pa = self.param_array[0].resolve(context)
            self.param_array = [template.Variable(x) for x in reduce(lambda x,y:x+y, pa)]

	filters = {}
#        nodes = BaseObject.nodes()
        ns = BaseObject.nodes().namespace()
        limit = 0

        for i in xrange(len(self.param_array)/2):
            try:
                k = self.param_array[2*i].resolve(context)
            except template.VariableDoesNotExist, E:
                k = eval('u"%s"'%str(self.param_array[2*i]))
            try:
                v = self.param_array[2*i+1].resolve(context)
            except template.VariableDoesNotExist, E:
                v = eval('SafeUnicode(u"%s")'%str(self.param_array[2*i+1]))

            if k not in ns: continue

            if k == u"limit": 
                limit = int(v)
            elif k in (u'cascade', u'foruser'):
#                nodes = eval('''nodes.%s()'''%k)
		filters[str(k)] = True
	    elif k == u'search':
		filters['search'] = eval(''' u'%s' ''' % v)
            elif type(v) == SafeUnicode:
#                nodes = eval('''nodes.%s(u"%s")'''%(k,v))
		if not filters.has_key(str(k)):	filters[str(k)] = []
		filters[str(k)].append(eval(''' u'%s' ''' % v))
            else:
#                nodes = eval('''nodes.%s("%s")'''%(k,v))
		if not filters.has_key(str(k)):	filters[str(k)] = []
		filters[str(k)].append(eval(''' '%s' ''' % v))

	print 'FILTERS', filters
	nodes = BaseObject.nodes(**filters)

        if limit>0:
            context[self.var] = nodes.limit(limit)
        else:
            context[self.var] = nodes.all()
        
        return ''

                

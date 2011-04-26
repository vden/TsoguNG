from django import template
import simplejson, urllib2, urlparse, httplib
from django.core.cache import cache
try: import hashlib
except: import md5 as hashlib

register = template.Library()

@register.tag
def gjson(parser, token):
	try:
		param_array = token.split_contents()
		tag = param_array[0]
		var = param_array[-1]
		params = param_array[1:-2]
	except ValueError:
		raise template.TemplateSyntaxError, "%r tag requires even number of arguments or array" % token.contents.split()[0]
	print "QQQ", params
	return GjsonNode(params, var)

class GjsonNode(template.Node):
	def __init__(self, params, var):
		print "WWW", var
		self.params = params
		self.var = var

	def render(self, context):
		res = []
		for x in self.params:
			try:
				res.append(template.Variable(x).resolve(context))
			except:
				pass

		url = ''.join([x.strip('"') for x in res])
		print "GET JSON FROM:", url

		try:
			req = urllib2.Request(url)
			httpdata = urllib2.urlopen(req)

		except urllib2.HTTPError, e:
			if e.code == 503:
				return e.readline()
			else:
				return e

		if httpdata.code==200:
			try:
				data = simplejson.load(httpdata)
			except:
				return u'Parsing json data error'
		else:
			return u'%s' % httpdata.read()

		context[self.var] = data
		return u''

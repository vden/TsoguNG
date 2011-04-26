# -*- coding:utf-8 -*-

from core.types import Log

def action(object, request):
	return {'logs': Log.objects.all().order_by('-date')[:100]}

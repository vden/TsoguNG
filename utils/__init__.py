#!/usr/bin/python
# -*- coding: utf-8 -*-

def deprecated(func):
	def fn(*args, **kwargs):
		print "Call to deprecated function %s from module %s" % (func.__name__, func.__module__)
		return func(*args, **kwargs)
	return fn

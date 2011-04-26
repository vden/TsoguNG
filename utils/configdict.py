# -*- coding: utf-8 -*-

from UserDict import UserDict
from core.models import Configlet

class ConfigDictReadOnlyException(Exception):
	pass

class ConfigDict(UserDict, object):
	def __init__(self, initialdata, obj):
		self.obj = obj
		super(ConfigDict, self).__init__(initialdata)

	def __setitem__(self, key, value):
		cfg = Configlet.objects.filter(bid=self.obj, predicate=key)
		if not len(cfg):
			cfg = Configlet(bid=self.obj, predicate=key)
		else:
			cfg = cfg[0]
		cfg.value=value
		cfg.save()
		super(ConfigDict, self).__setitem__(key, value)
		return cfg

	def __delitem__(self, key):
		cfg = Configlet.objects.filter(bid=self.obj, predicate=key)
		if len(cfg):
			cfg.delete()
		else:
			raise ConfigDictReadOnlyException
		super(ConfigDict, self).__delitem__(key)

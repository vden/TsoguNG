# -*- coding: utf-8 -*-

"""
	Менеджер объектов с жестким не инвалидируемым кешированием (для объектов-справочников)

	@author: Vlasov Dmitry
	@contact: scailer@veles.biz
	@contact: scailer@tsogu.ru
	@organization: TSOGU
	@status: функционирует 
	@version: 1.0a
"""

from django.db.models import Manager
from django.core.cache import cache
from core.decorators import simple_cache
import random

class HardCacheManager(Manager):
	""" Менеджер жесткого кеширования """

	def all(self):
#		print "ALL HARDCACHE"
		data = cache.get('hardcache_all_%s' % self.model.__name__)
		if not data:
#			print "GET HC: CREATE:", 'hardcache_all_%s' % self.model.__name__
			data = super(HardCacheManager, self).all()
			cache.set('hardcache_all_%s' % self.model.__name__, data, 24*60*60)
		return data
			
	def get(self, **kw):
#		print "GET HARDCACHE"
		data = cache.get('hardcache_get_%s_%s' % (self.model.__name__, hash(str(kw))))
		if not data:
#			print "GET HC: CREATE:", 'hardcache_get_%s_%s' % (self.model.__name__, hash(str(kw)))
			data = super(HardCacheManager, self).get(**kw)
			cache.set('hardcache_get_%s_%s' % (self.model.__name__, hash(str(kw))), data, 24*60*60)
#		print "GET HARDCACHE RES", kw, data
		return data

	def filter(self, **kw):
#		print "FILTER HARDCACHE"
		data = cache.get('hardcache_filter_%s_%s' % (self.model.__name__, hash(str(kw))))
		if not data:
#			print "FILTER HC: CREATE:", 'hardcache_filter_%s_%s' % (self.model.__name__, hash(str(kw)))
			data = super(HardCacheManager, self).filter(**kw)
			cache.set('hardcache_filter_%s_%s' % (self.model.__name__, hash(str(kw))), data, 24*60*60)
#		print "FILTER HARDCACHE RES", kw, data
		return data



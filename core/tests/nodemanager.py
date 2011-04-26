# -*- coding: utf-8 -*-

from django.utils.datastructures import MultiValueDict
import unittest
from django.test.client import Client
from django.test import TestCase
from core.models import *
from django.utils.http import urlencode
from datetime import datetime

class NodeManagerTest(TestCase):
#	fixtures = ['all_core.json','all_auth.json','banners_dump_initial.json']
	fixtures = ['all.json']

	def setUp(self):
		self.tag = Tag.objects.get(id=14)
		self.state = State.objects.get(id=1)
		pass

	def testBase(self):
		self.assertEquals(len(BaseObject.nodes().all()), len(BaseObject.objects.all()), 
				u'Некорректно выбранны все объекты')

	def testTag(self):
		self.assertEquals(len(BaseObject.nodes().tags(self.tag.id).all()), len(BaseObject.objects.filter(tags=Tag.objects.get(id=self.tag.id))), 
				u'Ошибка фильтрации по тегу заданному числом')
		self.assertEquals(len(BaseObject.nodes().tags(self.tag.name).all()), len(BaseObject.objects.filter(tags=Tag.objects.get(name=self.tag.name))), 
				u'Ошибка фильтрации по тегу заданному строкой')
		self.assertEquals(len(BaseObject.nodes().tags(self.tag).all()), len(BaseObject.objects.filter(tag=self.tag)), 
				u'Ошибка фильтрации по тегу заданному объектом')

	def testState(self):
		self.assertEquals(len(BaseObject.nodes().states(self.state.id).all()), len(BaseObject.objects.filter(tags=State.objects.get(id=self.state.id))), 
				u'Ошибка фильтрации по состоянию заданному числом')
		self.assertEquals(len(BaseObject.nodes().states(self.state.name).all()), len(BaseObject.objects.filter(tags=State.objects.get(name=self.state.name))), 
				u'Ошибка фильтрации по состоянию заданному строкой')
		self.assertEquals(len(BaseObject.nodes().states(self.state).all()), len(BaseObject.objects.filter(tags=self.state))), 
				u'Ошибка фильтрации по состоянию заданному объектом')




# -*- coding: utf-8 -*-

import unittest
from django.test.client import Client
from django.test import TestCase
from core.models import *
from django.utils.http import urlencode
from datetime import datetime

class NewsClientTest(TestCase):
	fixtures = ['all_core.json','all_auth.json','banners_dump_initial.json']
	no = News.objects.all()[0]

	def setUp(self):
		""" Клиентское тестирование новости """
		self.c = Client()
		self.c.login(username='admin', password='admin31415')
	
	def testGetView(self):
		""" Просмотр новости """
		resp = self.c.get(self.no.get_absolute_url())
		self.assertEquals(resp.status_code, 200)
#		resp = self.ca.get(self.no.get_absolute_url())
#		self.assertEquals(resp.status_code, 200)

	def testGetContent(self):
		""" Просмотр содержимого новости """
		resp = self.c.get(self.no.get_absolute_url(),{'form':'content'})
		self.assertEquals(resp.status_code, 200)
#		resp = self.ca.get(self.no.get_absolute_url(),{'form':'content'})
#		self.assertEquals(resp.status_code, 200)

	def testGetGeneral(self):
		""" Просмотр основных данных новости """
		resp = self.c.get(self.no.get_absolute_url(),{'form':'general'})
		self.assertEquals(resp.status_code, 200)
#		resp = self.ca.get(self.no.get_absolute_url(),{'form':'general'})
#		self.assertEquals(resp.status_code, 200)
	
	def testPostGeneral(self):
		""" Сохранение основных данных """
		resp = self.c.post(self.no.get_absolute_url(), {}, QUERY_STRING=urlencode({'form':'general'}, doseq=True))
		self.assertEquals(resp.status_code, 200)
		resp = self.c.post(self.no.get_absolute_url(), {'title':u'qwe', 'text':u'', 'category':[u'1']},QUERY_STRING=urlencode({'form':'general'}))
		self.assertEquals(resp.status_code, 200)
		resp = self.c.post(self.no.get_absolute_url(), {'title':u'asd', 'description':u'asd', 'text':u'qwe', 'category':[u'1']},QUERY_STRING=urlencode({'form':'general'}))
		self.assertEquals(resp.status_code, 200)

	def testGetExtra(self):
		""" Просмотр дополнителных данных новости """
		resp = self.c.get(self.no.get_absolute_url(),{'form':'extra'})
		self.assertEquals(resp.status_code, 200)
#		resp = self.ca.get(self.no.get_absolute_url(),{'form':'extra'})
#		self.assertEquals(resp.status_code, 200)

	def testPostExtra(self):
		""" Сохранение основных данных """
		resp = self.c.get(self.no.get_absolute_url(),{'form':'extra'})
		self.assertEquals(resp.status_code, 200)
#		resp = self.ca.get(self.no.get_absolute_url(),{'form':'extra'})
#		self.assertEquals(resp.status_code, 200)

	def testCloneTagTest(self):
		""" Проверка на самопроизвольное размножение тегов """
		tc_befor = Tag.objects.count()
		self.c.post(self.no.get_absolute_url(), {}, QUERY_STRING=urlencode({'form':'extra'}, doseq=True))
		tc = Tag.objects.count()
		self.assertEquals(tc, tc_befor)

	def testAddTagTest(self):
		""" Проверка корректного добавления тегов """
		tc_befor = Tag.objects.count()
		self.c.post(self.no.get_absolute_url(), {'new_tag':u'qwe'}, QUERY_STRING=urlencode({'form':'extra'}, doseq=True))
		tc = Tag.objects.count()
		self.assertEquals(tc, tc_befor+1)

	def testGetRights(self):
		""" Просмотр прав доступа новости """
		resp = self.c.get(self.no.get_absolute_url(),{'form':'extra'})
		self.assertEquals(resp.status_code, 200)
#		resp = self.ca.get(self.no.get_absolute_url(),{'form':'extra'})
#		self.assertEquals(resp.status_code, 200)



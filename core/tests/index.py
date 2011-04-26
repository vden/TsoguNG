# -*- coding: utf-8 -*-

from django.utils.datastructures import MultiValueDict
import unittest
from django.test.client import Client
from django.test import TestCase
from core.models import *
from django.utils.http import urlencode
from datetime import datetime


#class PageTest(TestCase):
#	fixtures = ['all_core.json','all_auth.json','banners_dump_initial.json']
#	
#	def setUp(self):
#		self.c = Client()
#		

class MyTest(TestCase):
	fixtures = ['all_core.json','all_auth.json','banners_dump_initial.json']

	def setUp(self):
		self.c = Client()
		self.c_admin = Client()
		self.c_admin.login(username='admin', password='admin31415')

	def testBasic(self):
		resp = self.c.get('/')
		self.assertEquals(resp.status_code, 200, u'Ошибка главной страницы')
	
	def testNews(self):
		print "+++",News.objects.all()[0].get_absolute_url()
		resp = self.c.get(News.objects.all()[0].get_absolute_url())
		self.assertEquals(resp.status_code, 200)#, u'Ошибка новости')
	
	def testEvent(self):
		resp = self.c.get(Event.objects.all()[0].get_absolute_url())
		self.assertEquals(resp.status_code, 200)#, u'Ошибка события')

	def testAddNewsGeneral(self):
		resp = self.c_admin.get('/news/university/new/News',{'form':'general'})
		self.assertEquals(resp.status_code, 200)

	def testFormNewsExtra(self):
		resp = self.c_admin.get(News.objects.all()[0].get_absolute_url(),{'form':'extra'})
		self.assertEquals(resp.status_code, 200)

	def testFormNewsContent(self):
		resp = self.c_admin.get(News.objects.all()[0].get_absolute_url(),{'form':'content'})
		self.assertEquals(resp.status_code, 200)

	def testFormNewsRight(self):
		resp = self.c_admin.get(News.objects.all()[0].get_absolute_url(),{'form':'rights'})
		self.assertEquals(resp.status_code, 200)

	def savePhotoWithoutTitle(self):
		f=open('core/fixtures/Screenshot.png')
		self.c_admin.post('/news/new/Photo',{'image':f},QUERY_STRING=urlencode({'form':'general'}, doseq=True))
		f.close()

	def copyFileProccess(self):
		ids = [u'%s'%x.id for x in News.objects.all()[:2]]
		self.c_admin.post('/news/university/',{'ids:list':ids,'folder_copy:method':u'asd'},QUERY_STRING=urlencode({'form':'content'}, doseq=True))
		self.c_admin.post('/news/university/',{'folder_copypaste:method':u'asd'},QUERY_STRING=urlencode({'form':'content'}, doseq=True))
	
	def postNews(self):
		self.c_admin.post('/news/university/new/News',{'title':u'Заголовок','category':u'1'},QUERY_STRING=urlencode({'form':'general'}, doseq=True))

	def testExtraFormPage(self):
		resp = self.c_admin.post(Page.objects.all()[0].get_absolute_url(),{'not_browse':True},QUERY_STRING=urlencode({'form':'extra'}, doseq=True))
		self.assertEquals(resp.status_code, 200)
	
	def textExtraFormNews(self):
		resp = self.c_admin.post(News.objects.all()[0].get_absolute_url(),{'not_browse':True,'date_published':'30.03.2009'},
				QUERY_STRING=urlencode({'form':'extra'}, doseq=True))
		self.assertEquals(resp.status_code, 200)
	
	def lastSlashTest(self):
		resp =self.c.get('/action/login/')
		self.assertEquals(resp.status_code, 200)
		n = News.objects.all()[0].get_absolute_url()
		resp = self.c.get(n[-1]!='/' and n+'/' or n)

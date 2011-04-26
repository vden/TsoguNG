# -*- coding: utf-8 -*-

"""
	Менеджер объектов с интерфейсом поиска через sphinx

	@author: Ivan Nikolaevich
	@contact: ivan.nikolaevich@gmail.com
	@contact: solit@tsogu.ru
	@organization: TSOGU
	@status: функционирует
"""

from django.db.models import Manager
import settings

class _BaseObjectManager(Manager):
	def search(self, query_str):
		""" Функция поиска
			@param query_str: строка для поиска в формате sphinx
			@type query_str: string
			@return: возращает queryset, при условии что все парамемты заданы правильно
			и в процессе импортирования модуля не возникли ошибки иначе вернет None
		"""
		try:
			from utils.sphinxapi import SphinxClient, SPH_MATCH_EXTENDED, SPH_SORT_RELEVANCE
		except ImportError:
			return None
		if query_str:
			sphinx = SphinxClient()
			sphinx.SetServer(settings.SPHINX_SERVER, settings.SPHINX_PORT)
			sphinx.SetMatchMode(SPH_MATCH_EXTENDED)
			sphinx.SetFieldWeights({'title':1000, 'slug':1000, 'description':500, 'page_text':100})
			sphinx.SetSortMode(SPH_SORT_RELEVANCE)
			sphinx.SetLimits(0, 1000)
			results = sphinx.Query(query_str)
			if results:
				ids = [m['id'] for m in results['matches']]
				results_objects = super(_BaseObjectManager, self).get_query_set().in_bulk(ids)
				results_objects = [results_objects[id] for id in ids if id in results_objects]
				return results_objects

	def look2root(self, location, inherit=False):
		from django.db import connection
		cursor = connection.cursor()
		cursor.execute('''select location, inherit, path from look2root(%d,%s);'''%(location, inherit))

		return dict(zip(('location', 'inherit', 'path'), cursor.fetchone()))

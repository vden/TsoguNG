# -*- coding: utf-8 -*-

"""
	Менеджер объектов с расширенным интерфейсом

	@author: Vlasov Dmitry
	@contact: scailer@veles.biz
	@contact: scailer@tsogu.ru
	@organization: TSOGU
	@status: функционирует 
	@version: 1.0

	@todo 1.1: Оптимизация среза, оптимизация поиска, кеширование
	@todo 1.2: Отложенное исполнение, доступ к queryset
"""

from django.db.models import Avg, Max, Min, Count
from django.utils.safestring import SafeUnicode


class NodeManager(object):
	""" Менеджер поиска/запросов по нодам сайта """
	query_set = None

	def __intelegance_check(self, array, cls, field='name'):
		""" 
			Функция приведениея объектов/строк/кодов к кодам объектов 
			@return: Массив кодов

			@param array: Массив объектов, строк и кодов
			@type array: array

			@param cls: Класс, которому принадлежат искомые коды объектов
			@type cls: Class
		"""
		res = []
		for x in array:
			if type(x) == int:
				res.append(x)
			elif type(x) in [unicode,str,SafeUnicode]:
				exec('''s = cls.objects.filter(%s=x)'''%field)
				if s: res.append(s[0].id)
			elif hasattr(x, 'id'):
				res.append(x.id)
			else:
				raise Exception('Unknown object type')
		return res

	def __call__(self, search=None, states=[], tags=[], types=[], sort_fields=[], parents=[], foruser=False, cascade=False,\
			authors=[], slugs=[], not_browse=None, no_cache=False):
		"""
			Функция инициации запроса/поиска.
			@return: Объект NodeManager (self)

			@param search: Строка запроса для поиска (выполняется в первую очередь)
			@type search: string

			@param states: Массив состояний объекта выраженный кодами, объектами State или юникодными строками имен
			@type states: array

			@param tags: Массив тегов объекта выраженный кодами, объектами State или юникодными строками имен
			@type tags: array

			@param types: Массив строк - имен классов 
			@type types: array

			@param sort_fields: Массив строк - полей для фильтрации
			@type sort_fields: array

			@param slugs: Массив строк - слагов объектов
			@type slugs: array

			@param authors: Массив пользователей выраженный кодами, объектами User, или юникодными строками имен
			@type authors: array

			@param not_browse: Фильтр по флагу «Просматриваемых объектов»
			@type not_browse: boolean

			@param foruser: Только типы, определенные для пользовательского просмотра
			@type foruser: boolean

			@param cascade: Анализировать вложенные объекты, при заданном предке (нереализовано)
			@type cascade: boolean 
		"""
		print 'CALL NODES'
		from core.models import BaseObject
		self.is_cascade = cascade
		if search:	self.query_set = BaseObject.objects.search(search)
		else:		self.query_set = BaseObject.objects.get_query_set()
		if foruser:	self.foruser()
		if types:	self.types(*types)
		if states:	self.states(*states)
		if tags:	self.tags(*tags)
		if parents:	self.parents(*parents)
		if sort_fields:	self.sort_fields(*sort_fields)
		if slugs:	self.slugs(*slugs)
		if authors:	self.authors(*authors)
		if not not_browse is None:	self.not_browse(not_browse)

		return self

	def in_bulk(self, data):
		"""
			Получает список объектов, по списку кодов и типов
		"""
		from core.portal.utils import get_type, UnknownPortalType
		from core.models import BaseObject
		from collections import defaultdict

		typed_data = defaultdict(list)
		[typed_data[x['type']].append(x['id']) for x in data]
		res = {}

		for type, values in typed_data.items():
			try:
				cls = get_type(type)
				res.update(cls.objects.in_bulk(values))
			except UnknownPortalType:
				pass

		return [res[x['id']] for x in data if res.has_key(x['id'])]

	def __get_results(self, limit=None, offer=None):
		""" 
			Функция, финализирующая запрос, получением результата.
			@return: list of portal objects
		"""
		if getattr(self, 'rating', False):
			d = [{'id':x.id,'type':x.type} for x in self.query_set[offer:limit]]
			return self.in_bulk(d)
		else:
			return self.in_bulk(self.query_set[offer:limit].values('id','type'))

	def all(self):
		""" 
			Функция, финализирующая запрос, получением результата, без ограничения по колличеству элементов
			@return: list of portal objects
		"""
		return self.__get_results()

	def oldall(self):
		return [x.direct_cast() for x in self.query_set]

	def limit(self, limit=None, offer=None):
		"""
			Функция, финализирующая запрос, получением результата, с ограничением по длинне массива
			@return: list of portal objects
		"""
		return self.__get_results(limit, offer)

	def foruser(self):
		"""
			Прозрачная функция, устанавливающая флаг «только объекты пользователя»
			@return: NodeManager object
		"""
		from core import REGISTRUM
		usertypes = [k for k,v in REGISTRUM['types'].items() if v['user']]
		self.query_set = self.query_set.filter(type__in=usertypes)
		return self

	def cascade(self):
		"""
			Прозрачная функция, устанавливающая флаг «каскадный поиск».
			Данный метод должна предшествовать вызову метода parents().
			@return: NodeManager object
		"""
		self.is_cascade = True
		return self

	def _get_childs_cascade(self, parents=[], res=[]):
		"""
			Функция рекурсивно получает список из вложеных объектов
			@return: BaseObject's list

			@param parents: Список BaseObject-ов 
			@type parents: array

			@param parents: Список кодов
			@type parents: array
		"""
		from core.models import BaseObject 
		for x in parents:
			res.append(x.id)
			self._get_childs_cascade(parents=BaseObject.objects.filter(parent=x.id), res=res)
		return res


	def parents(self, *args):
		"""
			Прозрачная функция - фильтр по предкам
			@return: NodeManager object
			@example: BaseObject.nodes().parents('/news/',953,'/inst/inig/').all()
		"""
		res = []
		for x in args:
			if type(x) == int:
				from core.models import BaseObject 
				res.append(BaseObject.objects.get(id=x))
			elif type(x) in [str,unicode]:
				from core.views import get_object_by_url
				res.append(get_object_by_url(x))
			elif hasattr(x, 'id'):
				res.append(x)
		if self.is_cascade:
			res = self._get_childs_cascade(res, [])
		else:
			res = [x.id for x in res]
		self.query_set = self.query_set.filter(parent__in=res)
		return self 

	def types(self, *args):
		"""
			Прозрачная функция - фильтр по типам
			@return: NodeManager object
			@example: BaseObject.nodes().types('VideoFile','Poll','Page').all()
		"""
		self.query_set = self.query_set.filter(type__in=args)
		return self

	def states(self, *args):
		"""
			Прозрачная функция - фильтр по состояниям
			@return: NodeManager object
			@example: BaseObject.nodes().states(1,u'скрытый',State.objects.get(id=3)).all()
		"""
		from core.models import State
		res = self.__intelegance_check(args, State)
		self.query_set = self.query_set.filter(state__in=res)
		return self

	def tags(self, *args):
		"""
			Прозрачная функция - фильтр по тегам
			@return: NodeManager object
			@example: BaseObject.nodes().tags(1,u'ИНиГ',Tag.objects.get(id=3)).all()
		"""
		from core.types.support import Tag 
		res = self.__intelegance_check(args, Tag)
		self.query_set = self.query_set.filter(tags__in=res)
		return self

	def sort_fields(self, *args):
		"""
			Прозрачная функция. Устанавливает поля для сортировки
			@return: NodeManager object
			@example: BaseObject.nodes().sort_fields('date_created','-date_published')
		"""
		if '-rating' in args:
			self.rating = True
			self.query_set = self.query_set.annotate(qq=Avg('rating__rating_value')).filter(qq__isnull=False).order_by('-qq','-date_published')
		elif 'rating' in args:
			self.rating = True
			self.query_set = self.query_set.annotate(qq=Avg('rating__rating_value')).filter(qq__isnull=False).order_by('qq','-date_published')
		else:
			self.query_set = self.query_set.order_by(*args)
		return self

	def authors(self, *args):
		"""
			Прозрачная функция - фильтр по автору
			@return: NodeManager object
			@example: BaseObject.nodes().tags(1,'user2',User.objects.get(id=3)).all()
		"""
		from core.models import User
		res = self.__intelegance_check(args, User, field='username')
		self.query_set = self.query_set.filter(author__in=res)
		return self

	def not_browse(self, flag):
		""" 
			Прозрачная функция - фильтр по флагу «только просматриваемые»
			@return: NodeManager object
			@example: BaseObject.nodes().not_browse(True).all()
		"""
		self.query_set = self.query_set.filter(not_browse=flag)
		return self

	def slugs(self, *args):
		"""
			Прозрачная функция - фильтр по слагам
			@return: NodeManager object
			@example: BaseObject.nodes().slugs('news','inig','tii').all()
		"""
		self.query_set = self.query_set.filter(slug__in=args)
		return self

	def namespace(self):
		return (u"search", u"states", u"tags", u"types", u"sort_fields", \
				u"parents", u"foruser", u"cascade", u"author", u"limit",\
				u"authors", u"not_browse", u"slugs")

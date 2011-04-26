# -*- coding: utf-8 -*-

"""
	Менеджер файловых операций

	@author: Vlasov Dmitry
	@contact: scailer@veles.biz
	@contact: scailer@tsogu.ru
	@organization: TSOGU
	@status: production
	@version: 1.0

	@todo 1.0: Каскадный поиск объектов
"""


from utils.messages import PortalMessage

class FileProcessor(object):

	obj_list = []

	def __init__(self, obj):
		""" 
			Инициализируем метод-объект 
				obj = <BaseObject> - рендериемый объект
		"""
		self.obj = obj				# <BaseObject>

	def __call__(self, request):
		self.request = request
		if request.method == 'POST':
			if request.POST.has_key('folder_cut:method'):
				self.get_bids()
				self.cut()
			elif request.POST.has_key('folder_delete:method'):
				self.get_bids()
				self.remove()
			elif request.POST.has_key('folder_copy:method'):
				self.get_bids()
				self.copy()
			elif request.POST.has_key('folder_copypaste:method'):
				self.get_objects()
				self.paste('copy')
			elif request.POST.has_key('folder_cutpaste:method'):
				self.get_objects()
				self.paste('cut')
			elif request.POST.has_key('folder_position:method'):
				self.save_position()
			else: return False
			self.request.method = 'GET'
			return self.request
		else: return False

	def set_portal_message(self, mes):
		self.request.portal_message.append(mes)

	def get_bids(self):
		if self.request.POST.has_key('ids:list') and self.request.POST['ids:list']:
			self.bids = [int(x) for x in self.request.POST.getlist('ids:list')]#.split(',')]
			self.request.session['bids'] = self.bids
			self.get_objects()

	def get_objects(self):
		from core.models import BaseObject
		self.obj_list = [x.direct_cast() for x in BaseObject.objects.filter(id__in = self.request.session['bids'])]

	def save_position(self):
		from core.models import BaseObject
		if self.request.POST.has_key('bids') and self.request.POST['bids']:
			list = self.request.POST['bids'].split(',')
			objs = {}
			for o in BaseObject.objects.filter(id__in = list):
				objs[str(o.id)]=o
			for x in enumerate(list):
				objs[x[1]].position=x[0]
				objs[x[1]].save()
			self.set_portal_message(PortalMessage(u'Порядок сохранен').set_property(type='message'))

	def cut(self):
		for x in self.obj_list:
			if x.block: self.set_portal_message(PortalMessage(u'Объект %s заблокирован'%x.title).set_property(type='warning'))
			else:
				if x.lock(self.request): 
					self.set_portal_message(PortalMessage(u'Объект %s вырезан'%x.title).set_property(type='message'))
					self.request.session['process'] = 'cut'
				else: self.set_portal_message(PortalMessage(u'Объект %s не может быть заблокирован'%x.title).set_property(type='error'))
		return True

	def copy(self):
		for x in self.obj_list:
			self.set_portal_message(PortalMessage(u'Объект %s скопирован'%x.title).set_property(type='message'))
			self.request.session['process'] = 'copy'
		return True

	def looptest(self, process_objects, curent_object):
		""" Проверка, дабы умудренные своей тупостью юзеры не делали необдуманных поступков, не создавали петель в дереве объектов. """
		for process_object in process_objects:
			if process_object.id in [x.id for x in curent_object.walktree()]:
				return False
		return True

	def paste(self, mode=None):
		if not self.looptest(self.obj_list, self.obj):
			self.set_portal_message(PortalMessage(u'Объект не может быть перемещен в своего потомка').set_property(type='error'))
			return True

		for x in self.obj_list:
			if x.unlock(self.request): 
				if mode == 'copy':
					self.tree_copy(x,self.obj)
					self.set_portal_message(PortalMessage(u'Объект %s вставлен'%x.title).set_property(type='complete'))
					self.request.session['bids'] = []
					self.request.session['process'] = ''
				elif mode == 'cut': 
					x.parent = self.obj
					x.save()
					self.set_portal_message(PortalMessage(u'Объект %s перемещен'%x.title).set_property(type='complete'))
					self.request.session['bids'] = []
					self.request.session['process'] = ''
				else: pass
			else: self.set_portal_message(PortalMessage(u'Объект %s не может быть разблокирован'%x.title).set_property(type='error'))
		return True

	def tree_copy(self, obj, parent):
		""" Производит рекурсивное копирование дерева объектов """
		obj_befor = obj
		from core.models import BaseObject
		# Определяем следующий pk
		bo_list = BaseObject.objects.filter(id__gt=obj.id).order_by('-id')
		obj.id = len(bo_list)>0 and int(bo_list[0].id)+1 or obj.id+1

		if obj.parent == parent:
			obj.slug = 'copy_of_' + obj.slug
		obj.parent = parent
		obj.save(force_insert=True)

		for x in obj_befor.get_child_nodes():
			self.tree_copy(x,obj)

	def delete(self):
		for x in self.obj_list:
			if x.block: 
				self.set_portal_message(PortalMessage(u'Объект %s заблокирован'%x.title).set_property(type='warning'))
			else:
				x.delete()
				self.set_portal_message(PortalMessage(u'Объект %s удален'%x.title).set_property(type='complete'))
				self.request.session['bids'] = []
				self.request.session['process'] = ''
		return True

	def remove(self):
		from core.types.support import State
		from core.models import BaseObject

		for x in self.obj_list:
			if x.block: 
				self.set_portal_message(PortalMessage(u'Объект %s заблокирован'%x.title).set_property(type='warning'))
			else:
				x._remove()
				self.set_portal_message(PortalMessage(u'Объект %s удален'%x.title).set_property(type='complete'))

		self.request.session['bids'] = []
		self.request.session['process'] = ''
		self.set_portal_message(PortalMessage(u'Для востановления случайно удаленных объектов обратитесь по электронной почте в службу поддержки ').set_property(type='warning'))
		return True

	def change_status(self):
		for x in self.obj_list:
			x
		return True

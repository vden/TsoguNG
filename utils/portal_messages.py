# -*- coding: utf-8 -*-

from utils.messages import PortalMessage
from core.middleware.threadlocals import set_portal_message

portal_messages = {
	'1':PortalMessage(u'Объект заблокирован').set_property(type='warning'),
	'comment_thanks': PortalMessage(u'Спасибо за Ваш комментарий! После рассмотрения модератором он будет опубликован!'),
	'trash_repear_error':PortalMessage(u'Объект востановлению не подлежит').set_property(type='error'),
	'trash_repear':PortalMessage(u'Объект востановлен').set_property(type='complete'),
	'trash_delete':PortalMessage(u'Объект удален').set_property(type='complete'),
	'account_complete':PortalMessage(u'Вы успешно зарегистрированы.').set_property(type='complete'),
}

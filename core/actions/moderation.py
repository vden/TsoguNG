# -*- coding:utf-8 -*-

from core.portal.register import portalaction
from core.portal.render import render_as_redirect

@portalaction(verbose_name=u'Модерирование комментариев', category='user', condition="u'Moderator' in groups")
@render_as_redirect()
def moderation(request):
	return '/comments/moderation/'

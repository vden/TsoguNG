# -*- coding: utf-8 -*-

from core.portal.register import portalaction
from core.portal.render import render_to_portal

@portalaction(verbose_name=u'Запрос песни на радио')
@render_to_portal(template='actions/songrequest.html')
def songrequest(request):
	post = request.POST
	try:
		req_name = post['req_name']
		req_group = post['req_group']
		req_addr = post['req_addr']
		req_song = post['req_song']
		req_text = post['req_text']
	except:
		return {'error': u'Одно из необходимых полей заявки не заполнено!'}

	subject = u"Заказ песни на радио (%s)"%req_song
	text = u"""
%(req_name)s (%(req_group)s) хочет, чтобы для %(req_addr)s поставили на радио песню "%(req_song)s" и пишет следующее:\n
%(req_text)s.

--
С уважением,
искусственный интеллект портала ТюмГНГУ.
"""%locals()

	from django.core.mail import send_mail
	from tsogung import settings
	send_mail(subject, text, settings.DEFAULT_FROM_EMAIL, [settings.RADIO_EMAIL,], fail_silently=True)

	return {'subject': subject, 'body': text}

# -*- coding: utf-8 -*-

from core.types import News
from core.types.support import Category
from core.views import get_object_by_url
from core.decorators import text_response
from utils.exceptions import ExceptionProcessor, Http403
from django.contrib.auth.models import User
from urllib import unquote_plus

@text_response
def action(object, request):
    try:
        title = unquote_plus(request.GET['title'])
        src = request.GET['src']
        url = request.GET['url']
        slug = request.GET['id']
    except:
        raise Http403

    if str(src) != "imib": raise Http403

    text=u'''Полный текст новости расположен по ссылке: <a href="%s" target="blank">%s</a>'''%(url,url)
    p = News(parent=get_object_by_url("/news/university/"), title=u"%s"%title, description=u' ', text=text, 
             author=User.objects.get(username="manger"), slug=slug ) 
    p.category = Category.objects.get(name=u"Новости ИМиБ")
    p.save()

    return p.get_absolute_url()

# -*- coding: utf-8 -*-

from core.views import get_object_by_url

# Явный objectaction
def action(object, request):
    path_info = request.session['old_request']['path_info']
    obj = get_object_by_url ( "/%s/"%path_info )
    
    return { 'title': obj.title, 'pid': path_info == '/' and "1793" or "/%s/"%path_info }

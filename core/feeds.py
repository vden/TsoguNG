# -*- coding: utf-8 -*-

from django.contrib.syndication.feeds import Feed
from core.models import BaseObject
from core.views import get_object_by_url

class ObjectFeed(Feed):
    portal_url = "http://www.tsogu.ru"
    
    def title(self, obj):
        return obj.title

    def link(self, obj):
        return obj.get_absolute_url()

    def item_link(self, obj):
        return self.portal_url+obj.get_absolute_url()
    
    def get_object(self, bits):
        return get_object_by_url("/".join(bits))

    def item_pubdate(self, obj):
        return obj.date_published or obj.date_modified
    
    def item_guid(self, obj):
        return str(obj.id)
    
    def item_categories(self, obj):
        try:
            return [ obj.direct_cast().category.name, ]
        except:
            return []

    def items(self, obj):
        blob_objects = obj.get_child_nodes(for_user=True, sort_field='-date_published', count=30, 
                                           states = [u"на главной", u"опубликованный"])
        if self.request.rss_type_name != '':
            blob_objects = [x for x in blob_objects if x.get_class_name() == self.request.rss_type_name ]
        return blob_objects

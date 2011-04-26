from django.contrib import admin
from banners.models import *
from django.contrib.contenttypes.models import ContentType

class BannerGroupAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ['name',]
admin.site.register(BannerGroup, BannerGroupAdmin)

class BannerAdmin(admin.ModelAdmin):
	list_display = ('image', 'title', 'effective_date', 'expire_date', 'new_window')
	search_fields = ['title', ]
	list_filter = ('groups',)
admin.site.register(Banner, BannerAdmin)

class TextBannerAdmin(admin.ModelAdmin):
	list_display = ( 'title', 'effective_date', 'expire_date', 'new_window', 'color')
	search_fields = ['title', ]
admin.site.register(TextBanner, TextBannerAdmin)

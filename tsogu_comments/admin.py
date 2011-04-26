# -*- coding: utf-8 -*-

from models import Comment
from django.contrib import admin
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from datetime import datetime as dt

class CommentAdmin(ForeignKeyAutocompleteAdmin):
	fieldsets = (
		(None,
		   {'fields': ('author', 'username', 'email', 'date_created', 'text', 'is_public', 'is_remove')}
		),
		('Meta',
		   {'fields': ('base_object', 're', 'date_moderation', 'moderator')}
		),
	)
	list_display = ('username', 'author', 'text', 'date_created', 'is_public', 'is_remove')
	related_search_fields = {'author':('username',)}
	date_hierarchy = 'date_created'
	list_filter = ('date_created', 'date_moderation', 'is_public', 'is_remove')
	readonly_fields = ('moderator', 'date_moderation', 're', 'base_object', 'date_created', 'author')
	search_fields = ('username', 'author__username')

	def save_model(self, request, obj, form, change):
		if not change: return
		old = self.get_object(request, obj.id)
		if (obj.is_public or obj.is_remove) and (obj.is_public != old.is_public or obj.is_remove != old.is_remove):
			obj.moderator = request.user
			obj.date_moderation = dt.now()
		obj.save()
admin.site.register(Comment, CommentAdmin)

# -*- coding: utf-8 -*-

from django.contrib import admin
from models import *
from django_extensions.admin import ForeignKeyAutocompleteAdmin

class TokenAdmin(admin.ModelAdmin):
	list_display = ('token','user_groups','date')
admin.site.register(Token, TokenAdmin)

class UserGroupsAdmin(ForeignKeyAutocompleteAdmin):
	related_search_fields = {'user':('username',)}
	list_display = ('user','application')
admin.site.register(UserGroups, UserGroupsAdmin)

class ApplicationAdmin(admin.ModelAdmin):
	list_display = ('name',)
admin.site.register(Application, ApplicationAdmin)

class DelegateRightAdmin(ForeignKeyAutocompleteAdmin):
	related_search_fields = {'base_object':('title','slug'), 'user':('username',)}
	search_fields = ['base_object__title', 'base_object__slug', 'user__username']
	list_display = ('base_object', 'group', 'user')
admin.site.register(DelegateRight, DelegateRightAdmin)

class ObjectPermissionsAdmin(ForeignKeyAutocompleteAdmin):
	related_search_fields = {'base_object':('title', 'slug')}
	list_display = ('base_object', 'permission', 'group')
admin.site.register(ObjectPermissions, ObjectPermissionsAdmin)

class ResponsibilityAdmin(ForeignKeyAutocompleteAdmin):
	related_search_fields = {'base_object':('title', 'slug')}
	list_display = ('base_object', 'position', 'user', 'telephone')
	search_fields = ('base_object__id', 'base_object__title', 'base_object__slug', 'user', 'position')
admin.site.register(Responsibility, ResponsibilityAdmin)

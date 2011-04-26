# -*- coding: utf-8 -*-

from django.contrib import admin
#from core.models import *
from django.contrib.contenttypes.models import ContentType
from django_extensions.admin import ForeignKeyAutocompleteAdmin
from django.contrib.admin import widgets as admin_widgets

from core.types import *
from core.types.post import PostTag
from core.models import BaseObject, Configlet, Viewlet, Rating, Alias
from core.types.support import State, StateTransform, Tag, TemplateView, Category
from core.registries import JSRegistry, CSSRegistry
from django.contrib.auth.models import Permission

class StateAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ['name',]
admin.site.register(State, StateAdmin)


class StateTransformAdmin(admin.ModelAdmin):
	list_display = ('slug', 'from_state','to_state','method','types')
	search_fields = ['from_state',]
admin.site.register(StateTransform, StateTransformAdmin)

class PostTagAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ['name',]
admin.site.register(PostTag, PostTagAdmin)

class TagAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ['name',]
admin.site.register(Tag, TagAdmin)

class TemplateViewAdmin(admin.ModelAdmin):
	list_display = ('template_type','name','path')
admin.site.register(TemplateView, TemplateViewAdmin)

class BaseObjectAdmin(ForeignKeyAutocompleteAdmin):
	related_search_fields = {'parent':('title', 'slug'), 'author':('username',)}
	list_display = ('title','author','state')
	search_fields = ['title', 'slug']
admin.site.register(BaseObject, BaseObjectAdmin)

class PageTemplateAdmin(ForeignKeyAutocompleteAdmin):
	related_search_fields = {'parent':('title', 'slug'), 'author':('username',)}
	list_display = ('title','template')
	search_fields = ['title',]
admin.site.register(PageTemplate, PageTemplateAdmin)

class PhotoAdmin(admin.ModelAdmin):
	list_display = ('image',)
	list_display = ('title','author', 'date_published', 'date_created')
	list_filter = ('date_published','date_created')
admin.site.register(Photo, PhotoAdmin)

class LinkAdmin(admin.ModelAdmin):
	list_display = ('title', 'slug', 'url', 'link_type')
admin.site.register(Link, LinkAdmin)

class FileAdmin(admin.ModelAdmin):
	list_display = ('title', 'path',)
admin.site.register(File, FileAdmin)

class PageAdmin(ForeignKeyAutocompleteAdmin):
	related_search_fields = {'parent':('title','slug'), 'author':('username',)}
	list_display = ('title', 'author','date_published')
	list_filter = ('date_published',)
	ordering = ('-date_published',)
	search_fields = ['title',]
admin.site.register(Page, PageAdmin)

class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ['name',]
admin.site.register(Category, CategoryAdmin)

class NewsAdmin(ForeignKeyAutocompleteAdmin):
	related_search_fields = {'parent':('title', 'slug'), 'author':('username',)}
	list_display = ('title','author', 'date_published', 'date_created')
	list_filter = ('date_published','date_created')
	ordering = ('-date_published',)
	search_fields = ['title',]
admin.site.register(News, NewsAdmin)

class EventAdmin(admin.ModelAdmin):
	list_display = ('title','author')
	search_fields = ['title',]
admin.site.register(Event, EventAdmin)

class ViewletAdmin(ForeignKeyAutocompleteAdmin):
	related_search_fields = {'bid':('title', 'slug'), 'user':('username',)}
	list_display = ('bid','position', 'block', 'inherits', 'user')
admin.site.register(Viewlet, ViewletAdmin)

class ConfigletAdmin(ForeignKeyAutocompleteAdmin):
	related_search_fields = {'bid':('title', 'slug')}
	list_display = ('bid','predicate')
	search_fields = ['bid__title', 'bid__slug']
admin.site.register(Configlet, ConfigletAdmin)

class JSRegistryAdmin(admin.ModelAdmin):
	list_display = ('path', 'condition', 'position')
	ordering = ('position',)
admin.site.register(JSRegistry, JSRegistryAdmin)

class CSSRegistryAdmin(admin.ModelAdmin):
	list_display = ('path', 'condition', 'position')
	ordering = ('position',)
admin.site.register(CSSRegistry, CSSRegistryAdmin)

class PermissionAdmin(admin.ModelAdmin):
	list_display = ['name', 'codename', 'content_type']
	search_fields = ['name', 'codename']
	list_filter = ('content_type',)
admin.site.register(Permission, PermissionAdmin)

class ContentTypeAdmin(admin.ModelAdmin):
	pass
admin.site.register(ContentType, ContentTypeAdmin)

class PollAdmin(admin.ModelAdmin):
	pass
admin.site.register(Poll, PollAdmin)

class PollChoiceAdmin(admin.ModelAdmin):
	pass
admin.site.register(PollChoice, PollChoiceAdmin)

class PollVoteAdmin(admin.ModelAdmin):
	pass
admin.site.register(PollVote, PollVoteAdmin)

class LogAdmin(admin.ModelAdmin):
	pass
admin.site.register(Log, LogAdmin)

class AliasAdmin(ForeignKeyAutocompleteAdmin):
	related_search_fields = {'bid':('title', 'slug')}
	list_display = ('url', 'bid')
admin.site.register(Alias, AliasAdmin)

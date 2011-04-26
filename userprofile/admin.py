# -*- coding: utf-8 -*-

from django.contrib import admin
from userprofile.models import *
from django_extensions.admin import ForeignKeyAutocompleteAdmin

class ProfileAdmin(ForeignKeyAutocompleteAdmin):
	related_search_fields = {'user':('username',)}
	list_display = ('user', 'student_id')
	search_fields = ('user__username', 'user__email')
admin.site.register(Profile, ProfileAdmin)

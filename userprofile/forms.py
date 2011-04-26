# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from models import Profile

class ProfileForm(forms.Form):
	last_name = User._meta.get_field("last_name").formfield()
	first_name = User._meta.get_field("first_name").formfield()
	middle_name = Profile._meta.get_field("middle_name").formfield()
	email = User._meta.get_field("email").formfield()
	subscription = Profile._meta.get_field("subscription").formfield()

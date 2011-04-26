# -*- coding: utf-8 -*-

from models import Comment
from django import forms

class CommentForm(forms.ModelForm):
	class Meta:
		model = Comment
		fields = ('username', 'email', 'text', 'base_object', 're')
		widgets = {
				'base_object': forms.HiddenInput(),
				're': forms.HiddenInput(),
				'text': forms.Textarea(),
		}

	def clean(self):
		cleaned_data = self.cleaned_data
		bo = cleaned_data.get("base_object")
		re = cleaned_data.get("re")
		if re and (not re.is_public or re.base_object != bo):
			raise forms.ValidationError(u"Комментария на который вы пытаетесь ответить нет, либо он не опубликован.")
		return cleaned_data

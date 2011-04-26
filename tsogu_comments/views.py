# -*- coding: utf-8 -*-

from forms import CommentForm
from models import Comment
from core.portal.render import render_to_portal, render_ajax
from django.template import RequestContext, loader as template_loader
from rights import has_access
from core.portal.exceptions import Http403

@render_ajax(type='html')
def add(request):
	user = request.user
	if request.method == 'GET':
		initial = {}
		if user.is_authenticated():
			try:
				profile = request.user.get_profile()
			except:
				profile = None
			initial['username'] = ' '.join([name for name in user.last_name, user.first_name, getattr(profile, 'middle_name', '') if name])
			if not initial['username']: initial['username'] = request.user.username
			initial['email'] = request.user.email
		initial['base_object'] = request.GET.get('bid')
		initial['re'] = request.GET.get('re')
		form = CommentForm(initial=initial)
	else:
		data = dict([(key, value.strip()) for key, value in request.POST.items()])
		form = CommentForm(data)
		if form.is_valid():
			comment = form.save()
			if user.is_authenticated():
				comment.author = user
				comment.save()
			return u"Спасибо за Ваш комментарий! После рассмотрения модератором он будет опубликован!<p><a href=''>Обновить страницу</a></p>"
	context = {'form': form}
	return template_loader.get_template("tsogu_comments_form.html").render(
			RequestContext(request, context))

@render_to_portal(template='comments_moderation.html', columns=('a', 'b'))
def moderation(request):
	if not has_access(request.user, 'can_moderate'): raise Http403(u'Недостаточно прав для модерации комментариев.')
	context = {}
	context['comments'] = Comment.objects.filter(is_public=False, is_remove=False)
	return context

@render_ajax()
def moderation_action(request, action):
	if not has_access(request.user, 'can_moderate'): raise Http403(u'Недостаточно прав для модерации комментариев.')
	comment_id = request.POST.get('comment_id')
	comment = Comment.objects.get(id=comment_id)
	return {'publish': comment.publish, 'remove': comment.remove}[action](request.user)

# -*- coding: utf-8 -*-

from django import template
from pytils import dt
from tsogung.tsogu_comments.models import Comment
register = template.Library()

@register.inclusion_tag('tsogu_comments.html', takes_context=True)
def comments(context):
	bo = context.get('object')
	comments = Comment.get_comments(bo)
	length = len(comments)
	thread = {}
	for comment in comments:
		thread.setdefault(getattr(comment.re, 'id', 0), []).append(comment)

	def html_thread(ul):
		html = u"<ul>"
		for li in ul:
			html += u'''<li><div class='comment'>
				<div class='comment-title'><b>%(username)s</b>, %(date)s написал(а):
					<a href="javascript:;" comment_id='%(id)s' class="local-link add_comment">Комментировать</a>
				</div>
				%(text)s</div>'''%{
						'username': li.username,
						'date': dt.ru_strftime(u"%d %B %Y г. в %H:%M", li.date_created, inflected=True),
						'text': li.text,
						'id': li.id}
			if li.id in thread:
				html += html_thread(thread[li.id])
			html += u"</li>"
		html += u"</ul>"
		return html
	html = html_thread(thread.get(0, []))

	return {'object': bo, 'length': length, 'html': html}

@register.simple_tag
def comments_count(bo):
	return Comment.get_comments_count(bo)

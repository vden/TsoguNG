# -*- coding: utf-8 -*

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login as djlogin
from core.portal.exceptions import Http302
from core.portal.register import portalaction
from core.portal.render import render_to_portal

@portalaction(verbose_name=u'Вход', category='user', condition='isAnonymous')
@render_to_portal(template='actions/login.html')
def login(request):
	logged_in = False
	errors = False
	if request.method == 'GET':
		frm = AuthenticationForm()
	else:
		frm = AuthenticationForm(data=request.POST)
		if frm.is_valid():
			djlogin(request, frm.get_user())
			if request.session.test_cookie_worked():
				request.session.delete_test_cookie()
			logged_in = True
			raise Http302(request.POST.get('next'))
		else:
			print "Errors: ", frm.errors
			errors = True

	# если у нас есть сохраненный путь -- переходим на него после логина
	# если логин с главной или пути нет -- переходим на рабочую зону
	next_page = request.GET.get('next', request.session.has_key('old_request') and request.session['old_request']['path'] or "/")
	next_page = next_page in ["/","/portal/logout/"] and "/portal/workspace/" or next_page
	    
	return {'frm': frm, 'logged_in': logged_in, 'errors': errors, 'next': next_page}

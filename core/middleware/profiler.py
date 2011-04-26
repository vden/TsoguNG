import sys
import tempfile
import hotshot
import hotshot.stats
from django.conf import settings
from cStringIO import StringIO

class ProfileMiddleware(object):
    """
    Displays hotshot profiling for any view.
    http://yoursite.com/yourview/?prof

    Add the "prof" key to query string by appending ?prof (or &prof=)
    and you'll see the profiling results in your browser.
    It's set up to only be available in django's debug mode,
    but you really shouldn't add this middleware to any production configuration.
    * Only tested on Linux
    """
    def process_request(self, request):
        if settings.DEBUG and request.GET.has_key('prof'):
            self.tmpfile = tempfile.NamedTemporaryFile()
            self.prof = hotshot.Profile(self.tmpfile.name)

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if settings.DEBUG and request.GET.has_key('prof'):
            return self.prof.runcall(callback, request, *callback_args, **callback_kwargs)

    def process_response(self, request, response):
        if settings.DEBUG and request.GET.has_key('prof'):
            self.prof.close()

            out = StringIO()
            old_stdout = sys.stdout
            #sys.stdout = out

            stats = hotshot.stats.load(self.tmpfile.name)
            #stats.strip_dirs()
            stats.sort_stats('time', 'calls')
            stats.print_stats()

            #sys.stdout = old_stdout
            stats_str = out.getvalue()

            if response and response.content and stats_str:
                response.content = "<pre>" + stats_str + "</pre>"

        return response








#from django.http import HttpResponse
#import hotshot, hotshot.stats
#import sys, StringIO, os
#
#class ProfileMiddleware():
#	def __init__(self):
#		pass
#
#	def process_view(self, request, view, *args, **kwargs):
#		for item in request.META['QUERY_STRING'].split('&'):
#			if item.split('=')[0] == 'profile': # profile in query string
#
#				# catch the output, must happen before stats object is created
#				# see https://bugs.launchpad.net/webpy/+bug/133080 for the details
#				std_old, std_new = sys.stdout, StringIO.StringIO()
#				sys.stdout = std_new
#
#				# now let's do some profiling
#				tmpfile = '/tmp/%s' % request.COOKIES['sessionid']
#				prof = hotshot.Profile(tmpfile)
#
#				# make a call to the actual view function with the given arguments
#				response = prof.runcall(view, request, *args[0], *args[1])
#				prof.close()
#
#				# and then statistical reporting
#				stats = hotshot.stats.load(tmpfile)
#				stats.strip_dirs()
#				stats.sort_stats('time')
#
#				# do the output
#				stats.print_stats(1.0)
#
#				# restore default output
#				sys.stdout = std_old
#
#				# delete file
#				os.remove(tmpfile)
#
#				return HttpResponse('<pre\>%s</pre>' % std_new.getvalue())
#
#			return None

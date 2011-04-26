from django.conf.urls.defaults import *
import views as tiny_views
urlpatterns = patterns('',
    #url(r'download/$', tiny_views.download),
    url(r'^$', tiny_views.all),
)

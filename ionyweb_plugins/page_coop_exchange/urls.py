# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from .views import index_view, detail_view, add_view, add_view2

urlpatterns = patterns('',
                       url(r'^$', index_view),
                       url(r'^exchanges_add/$', add_view),
                       url(r'^(?P<pk>[\w-]+)/$', detail_view),
                       )                          
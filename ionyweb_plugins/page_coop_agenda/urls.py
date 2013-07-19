# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from .views import index_view, detail_view, carto_view, add_view, reply_view, delete_view

urlpatterns = patterns('',
                       url(r'^$', index_view),
                       url(r'^carto/$', carto_view),
                       url(r'^event_add/$', add_view),
                       url(r'^event_reply/(?P<event_id>\d+)/$', reply_view),
                       url(r'^event_delete/(?P<event_id>\d+)/$', delete_view),
                       url(r'^event_edit/(?P<event_id>\d+)/$', add_view),                         
                       url(r'^(?P<pk>[\w-]+)/$', detail_view),
                       )
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from .views import index_view, carto_view, detail_view, add_view, reply_view, delete_view, get_org_infos

urlpatterns = patterns('',
                       url(r'^$', index_view),
                       url(r'^carto/$', carto_view),
                       url(r'^get_org_infos/(?P<org_id>\d+)/$', get_org_infos),
                       url(r'^exchange_reply/(?P<exchange_id>\d+)/$', reply_view),   
                       url(r'^exchange_delete/(?P<exchange_id>\d+)/$', delete_view),
                       url(r'^exchange_add/$', add_view),
                       url(r'^exchange_edit/(?P<exchange_id>\d+)/$', add_view),  
                       url(r'^(?P<pk>[\w-]+)/$', detail_view),
                       )                          
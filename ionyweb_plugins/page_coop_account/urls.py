# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from .views import index_view, detail_view, logout_view, mailing_view, editpref_view, register_view, password_reset_view, password_reset_done_view, password_reset_confirm_view, password_reset_complete_view

urlpatterns = patterns('',
                       url(r'^$', index_view),
                       url(r'^logout/$', logout_view),
                       url(r'^register/$', register_view),
                       url(r'^password_reset/$', password_reset_view),
                       url(r'^password_reset_done/$', password_reset_done_view),
                       url(r'^password_reset_confirm/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
                            password_reset_confirm_view),
                       url(r'^password_reset_complete/$', password_reset_complete_view),                       
                       url(r'^mailing/$', mailing_view),
                       url(r'^(?P<pk>[\w-]+)/$', detail_view),
                       url(r'^pref_edit/(?P<user_id>\d+)/$', editpref_view),
                       )
                       

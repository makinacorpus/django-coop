# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from .views import index_view, detail_view, logout_view, mailing_view, editpref_view, register_view, activate_view
from .models import AccountActivationView

urlpatterns = patterns('',
                       url(r'^$', index_view),
                       url(r'^logout/$', logout_view),
                       url(r'^register/$', register_view),
                       url(r'^mailing/$', mailing_view),
                       url(r'^(?P<pk>[\w-]+)/$', detail_view),
                       url(r'^pref_edit/(?P<user_id>\d+)/$', editpref_view),
                       )
                       

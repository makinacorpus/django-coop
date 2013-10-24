# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from .views import index_view, export

urlpatterns = patterns('',
                       url(r'^$', index_view),
                       url(r'^export/$', export),
                       )
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from .views import index_view, carto_view

urlpatterns = patterns('',
                       url(r'^$', index_view),
                       url(r'^carto/$', carto_view),
                       )                          
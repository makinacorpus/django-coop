# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, url
from django.contrib.auth import views as auth_views

urlpatterns = patterns('coop.rdf.views',

    url(r'^import/$', 'rdf_import'),

)

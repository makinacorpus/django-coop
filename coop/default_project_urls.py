# -*- coding:utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
import sys

# https://code.djangoproject.com/ticket/10405#comment:11
# from django.db.models.loading import cache as model_cache
# if not model_cache.loaded:
#     model_cache.get_models()

from coop_local.urls import urlpatterns

handler500 = 'coop.views.SentryHandler500'

urlpatterns += patterns('',
    
    url(r'^', include('scanredirect.urls')),

    url(r'^admin_tools/', include('admin_tools.urls')),
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/password_reset/$', 'django.contrib.auth.views.password_reset', name='admin_password_reset'),
    url(r'^admin/password_reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm'),
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete'),
    #url(r'^org/$', 'coop_local.views.org_list', name="org_list"),  # exemple de view django-coop surchargee
    url(r'^selectable/', include('selectable.urls')),
)


# for local testing
if settings.DEBUG or ('runserver' in sys.argv):
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )


if 'coop_tag' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^', include('coop_tag.urls')),
    )

if 'coop.agenda' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^', include('coop.agenda.urls')),
    )

if 'coop.project' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^', include('coop.project.urls')),
    )

if 'coop.mailing' in settings.INSTALLED_APPS:
    urlpatterns += patterns('',
        (r'^', include('coop.mailing.urls')),
    )

urlpatterns += patterns('',
    (r'^forms/', include('forms_builder.forms.urls')),
    (r'^', include('coop_geo.urls', app_name='coop_geo')),
    (r'^', include('coop.urls')),
)

# Ionyweb
urlpatterns += patterns('',
    (r'^', include('ionyweb.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
    # url(r'^', include('debug_toolbar_htmltidy.urls'))
    # url(r'^', include('debug_toolbar_user_panel.urls')),
)

# -*- coding: utf-8 -*-

from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from coop_local.models import Event, EventCategory, Calendar, Occurrence
from django.conf import settings

from django.shortcuts import get_object_or_404

from ionyweb.website.rendering.medias import CSSMedia
from datetime import datetime

from .forms import PageApp_CoopAccountForm

from django.db.models import Q

from django.contrib.gis import geos
from django.contrib.gis.measure import D
from coop_local.models import Location

from django.contrib.auth import authenticate, login



MEDIAS = (
    CSSMedia('page_coop_account.css'),
    )

def index_view(request, page_app):
    base_url = u'%s' % (page_app.get_absolute_url())
    
    if request.method == 'POST': # If the login form has been submitted
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page.
            #else:
                # Return a 'disabled account' error message
    #else:
        # Return an 'invalid login' error message.
        
    
    
    if request.user.is_authenticated():
        render_page = 'page_coop_account/index.html'
        # TODO: gestion infos personnelles
        
        # TODO: gestion mes annonces / déposer une annonce / supprimer / valider..
        
        # TODO: gestion mes évènements / déposer ...
        
    else:
        render_page = 'page_coop_account/login.html'
    
        
    rdict = {'object': page_app, 'base_url': base_url}
    
    return render_view(render_page,
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))


def detail_view(request, page_app, pk):
    event = get_object_or_404(Event, pk=pk)
    base_url = u'%sp/' % (page_app.get_absolute_url())
    rdict = {'object': page_app, 'e': event, 'media_path': settings.MEDIA_URL, 'base_url': base_url}
    return render_view('page_coop_account/detail.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))                              
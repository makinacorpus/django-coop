# -*- coding: utf-8 -*-

from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from coop_local.models import Exchange

from django.conf import settings

from django.shortcuts import get_object_or_404

from ionyweb.website.rendering.medias import CSSMedia
from datetime import datetime

from .forms import PageApp_CoopExchangeForm, PageApp_CoopExchangeNewForm

from django.db.models import Q

MEDIAS = (
    CSSMedia('page_coop_exchange.css'),
)

def index_view(request, page_app):
    base_url = u'%s' % (page_app.get_absolute_url())

    exchanges = Exchange.objects.all()

    if request.method == 'POST': # If the form has been submitted        
        # TODO: other filters
        form = PageApp_CoopExchangeForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['free_search']:
                exchanges = exchanges.filter(Q(title__contains=form.cleaned_data['free_search']) | Q(description__contains=form.cleaned_data['free_search']))
            
            if form.cleaned_data['type_exchange']:
                exchanges = exchanges.filter(Q(eway__in=form.cleaned_data['type_exchange']))

            if form.cleaned_data['type']:
                exchanges = exchanges.filter(Q(etype__in=form.cleaned_data['type']))

    else:
        form = PageApp_CoopExchangeForm() # An empty form
    
    center_map = settings.COOP_MAP_DEFAULT_CENTER
    
    rdict = {'exchanges': exchanges, 'base_url': base_url, 'form': form, 'center': center_map}
    
    return render_view('page_coop_exchange/index.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))                           

                       
def detail_view(request, page_app, pk):
    event = get_object_or_404(Exchange, pk=pk)
    base_url = u'%sp/' % (page_app.get_absolute_url())
    rdict = {'object': page_app, 'e': event, 'media_path': settings.MEDIA_URL, 'base_url': base_url}
    return render_view('page_coop_exchange/detail.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))


def add_view(request, page_app, pk):

    base_url = u'new_exchange'

    if request.method == 'POST': # If the form has been submitted        
        # TODO: other filters
        form = PageApp_CoopExchangeNewForm(request.POST)
        if form.is_valid():
            # TODO: save
            form.save()
    else:
        form = PageApp_CoopExchangeNewForm() # An empty form
    
    rdict = {'media_path': settings.MEDIA_URL, 'base_url': base_url, 'form': form}
    return render_view('page_coop_exchange/new.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))



                       
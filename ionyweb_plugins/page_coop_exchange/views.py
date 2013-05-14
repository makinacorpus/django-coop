# -*- coding: utf-8 -*-

from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from coop_local.models import Exchange

from django.conf import settings

from django.shortcuts import get_object_or_404

from ionyweb.website.rendering.medias import CSSMedia
from datetime import datetime

from .forms import PageApp_CoopExchangeForm, PartialExchangeForm

from django.db.models import Q

from django.contrib.gis import geos
from coop_local.models import Location
from math import pi


from coop.exchange.admin import ExchangeForm

MEDIAS = (
    CSSMedia('page_coop_exchange.css'),
)

def index_view(request, page_app):
    base_url = u'%s' % (page_app.get_absolute_url())

    exchanges = Exchange.objects.all()

    if request.method == 'POST': # If the form has been submitted        
        form = PageApp_CoopExchangeForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['free_search']:
                exchanges = exchanges.filter(Q(title__contains=form.cleaned_data['free_search']) | Q(description__contains=form.cleaned_data['free_search']))
            
            if form.cleaned_data['type_exchange']:
                exchanges = exchanges.filter(Q(eway__in=form.cleaned_data['type_exchange']))

            if form.cleaned_data['type']:
                exchanges = exchanges.filter(Q(etype__in=form.cleaned_data['type']))

            if form.cleaned_data['activity']:
                exchanges = exchanges.filter(Q(activity=form.cleaned_data['activity']))
            
            if form.cleaned_data['thematic']:
                exchanges = exchanges.filter(Q(transverse_themes=form.cleaned_data['thematic']))
            
            if form.cleaned_data['location']:
                coords = form.cleaned_data['location'].split(",")
                center = geos.Point(float(coords[0]), float(coords[1]))
                radius = form.cleaned_data['location_buffer']
                distance_degrees = (360 * radius) / (pi * 6378)
                zone = center.buffer(distance_degrees)
                
                 # Get the possible location in the buffer...
                possible_locations = Location.objects.filter(point__intersects=zone)
                # ...and filter organization according to these locations
                exchanges = exchanges.filter(Q(location__in=possible_locations))
            
            #TODO : mode
            
            #TODO : skills
            
    else:
        form = PageApp_CoopExchangeForm({'location_buffer': '10'}) # An empty form
    
    center_map = settings.COOP_MAP_DEFAULT_CENTER
    
    rdict = {'exchanges': exchanges, 'base_url': base_url, 'form': form, 'center': center_map}
    
    return render_view('page_coop_exchange/index.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))                           

                       
def detail_view(request, page_app, pk):
    e = get_object_or_404(Exchange, pk=pk)
    base_url = u'%sp/' % (page_app.get_absolute_url())
    rdict = {'object': page_app, 'e': e, 'media_path': settings.MEDIA_URL, 'base_url': base_url}
    return render_view('page_coop_exchange/detail.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))


def add_view(request, page_app):
    if request.user.is_authenticated():
        base_url = u'%sp/exchange_add' % (page_app.get_absolute_url())
        center_map = settings.COOP_MAP_DEFAULT_CENTER

        if request.method == 'POST': # If the form has been submitted        
            exchange = Exchange()
            form = PartialExchangeForm(request.POST, instance = exchange)
            
            if form.is_valid():
                exchange = form.save()
                base_url = u'%s' % (page_app.get_absolute_url())
                rdict = {'base_url': base_url}
                return render_view('page_coop_exchange/add_success.html',
                                rdict,
                                MEDIAS,
                                context_instance=RequestContext(request))
        else:
            form = PartialExchangeForm() # An empty form
        
        rdict = {'media_path': settings.MEDIA_URL, 'base_url': base_url, 'form': form, 'center': center_map}
        return render_view('page_coop_exchange/add.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request))
    else:
        return render_view('page_coop_exchange/forbidden.html')


                       
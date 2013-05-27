# -*- coding: utf-8 -*-

from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from coop_local.models import Exchange
from coop_local.models import Location

from django.conf import settings

from django.shortcuts import get_object_or_404

from ionyweb.website.rendering.medias import CSSMedia
from datetime import datetime

from .forms import PageApp_CoopExchangeForm, PartialExchangeForm

from django.db.models import Q

from django.contrib.gis import geos
from coop_local.models import Location
from math import pi
from django.utils.simplejson import dumps


from coop.exchange.admin import ExchangeForm

MEDIAS = (
    CSSMedia('page_coop_exchange.css'),
)

def index_view(request, page_app):
    rdict = filter_data(request, page_app)
    return render_view('page_coop_exchange/index.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))                           


def carto_view(request, page_app):
    rdict = filter_data(request, page_app)    
    return render_view('page_coop_exchange/index_carto.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request)) 


def filter_data(request, page_app):
    base_url = u'%s' % (page_app.get_absolute_url())

    exchanges = Exchange.objects.all()
    more_criteria = False
    
    if base_url == settings.COOP_EXCHANGE_SERVICES_URL:
        exchanges = exchanges.filter(organization__isnull=True)
        search_form_template = "page_coop_exchange/search_form_service.html"
    if base_url == settings.COOP_EXCHANGE_EXCHANGES_URL:
        exchanges = exchanges.filter(organization__isnull=False)
        search_form_template = "page_coop_exchange/search_form_exchange.html"
    
    if request.method == 'POST': # If the form has been submitted        
        form = PageApp_CoopExchangeForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['free_search']:
                exchanges = exchanges.filter(Q(title__contains=form.cleaned_data['free_search']) | Q(description__contains=form.cleaned_data['free_search']))
            
            if form.cleaned_data['type_exchange']:
                exchanges = exchanges.filter(Q(eway__in=form.cleaned_data['type_exchange']))

            if form.cleaned_data['type']:
                exchanges = exchanges.filter(Q(etype__in=form.cleaned_data['type']))

            if form.cleaned_data['thematic'] or form.cleaned_data['thematic2'] or form.cleaned_data['thematic3']:
                exchanges = exchanges.filter(Q(transverse_themes=form.cleaned_data['thematic']) | Q(transverse_themes=form.cleaned_data['thematic2']) | Q(transverse_themes=form.cleaned_data['thematic3']))
            
            if form.cleaned_data['activity'] or form.cleaned_data['activity2']:
                exchanges = exchanges.filter(Q(activity=form.cleaned_data['activity']) | Q(activity=form.cleaned_data['activity2']))
                
                
            if form.cleaned_data['location']:
                label = form.cleaned_data['location']
                location = get_object_or_404(Location, label=label)                
                center = geos.Point(float(location.point.x), float(location.point.y))
                radius = form.cleaned_data['location_buffer']
                distance_degrees = (360 * radius) / (pi * 6378)
                zone = center.buffer(distance_degrees)
                
                 # Get the possible location in the buffer...
                possible_locations = Location.objects.filter(point__intersects=zone)
                # ...and filter organization according to these locations
                exchanges = exchanges.filter(Q(location__in=possible_locations))
            
            #TODO : mode
            
            #TODO : skills
            
            #TODO : warranty
            
            #TODO : organization
            
    else:
        form = PageApp_CoopExchangeForm({'location_buffer': '10'}) # An empty form
        more_criteria = False
    
    center_map = settings.COOP_MAP_DEFAULT_CENTER
    
    # Get available locations for autocomplete
    available_locations = dumps([location.label for location in Location.objects.all()])
    
    rdict = {'exchanges': exchanges, 'base_url': base_url, 'form': form, 'center': center_map, 'more_criteria': more_criteria, 'available_locations': available_locations, "search_form_template": search_form_template}
    
    return rdict
                       
                       
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


                       
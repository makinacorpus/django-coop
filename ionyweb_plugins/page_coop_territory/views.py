# -*- coding: utf-8 -*-

from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from coop_local.models import Location

from django.conf import settings

from django.shortcuts import get_object_or_404

from ionyweb.website.rendering.medias import CSSMedia
from datetime import datetime

from .forms import PageApp_CoopTerritoryForm

from django.db.models import Q

from django.contrib.gis import geos
from coop_local.models import Location, Area, Document
from math import pi
from django.utils.simplejson import dumps

from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.core.mail import send_mail

MEDIAS = (
    CSSMedia('page_coop_territory.css'),
)

def index_view(request, page_app):
    rdict = filter_data(request, page_app, "list")
    return render_view('page_coop_territory/index.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))                           


def carto_view(request, page_app):
    rdict = filter_data(request, page_app, "carto")    
    return render_view('page_coop_territory/index_carto.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request)) 


def filter_data(request, page_app, mode):
    base_url = u'%s' % (page_app.get_absolute_url())

    #exchanges = Exchange.objects.all()
    #more_criteria = False
    
    items = []
    
    #exchanges = exchanges.filter(organization__isnull=True)
    search_form_template = "page_coop_territory/search_form_territory.html"
    
    if request.method == 'GET':  
        form = PageApp_CoopTerritoryForm(request.GET)
        #if form.is_valid():
            #if form.cleaned_data['free_search']:
                #exchanges = exchanges.filter(Q(title__contains=form.cleaned_data['free_search']) | Q(description__contains=form.cleaned_data['free_search']))
            
            #if form.cleaned_data['type_exchange']:
                #exchanges = exchanges.filter(Q(eway__in=form.cleaned_data['type_exchange']))

            #if form.cleaned_data['type']:
                #exchanges = exchanges.filter(Q(etype__in=form.cleaned_data['type']))

            #if form.cleaned_data['thematic'] or form.cleaned_data['thematic2']:
                #exchanges = exchanges.filter(Q(transverse_themes=form.cleaned_data['thematic']) | Q(transverse_themes=form.cleaned_data['thematic2']))
            
            #if form.cleaned_data['activity'] or form.cleaned_data['activity2']:
                #exchanges = exchanges.filter(Q(activity=form.cleaned_data['activity']) | Q(activity=form.cleaned_data['activity2']))
                
                
            #if form.cleaned_data['location']:
                #label = form.cleaned_data['location']
                #pk = form.cleaned_data['location_id']
                #area = get_object_or_404(Area, pk=pk)
                #radius = form.cleaned_data['location_buffer']
                #distance_degrees = (360 * radius) / (pi * 6378)
                #zone = area.polygon.buffer(distance_degrees)
                 ## Get the possible location in the buffer...
                #possible_locations = Location.objects.filter(point__intersects=zone)
                ## ...and filter organization according to these locations
                #exchanges = exchanges.filter(Q(location__in=possible_locations))
            
            ##TODO : mode
            
            ##TODO : skills
    else:
        form = PageApp_CoopTerritoryForm({'location_buffer': '10'}) # An empty form
        more_criteria = False
    
    center_map = settings.COOP_MAP_DEFAULT_CENTER
    
    paginator = Paginator(items, 10)
    page = request.GET.get('page')
    try:
        items_page = paginator.page(page)
    except PageNotAnInteger:
        items_page = paginator.page(1)
    except EmptyPage:
        items_page = paginator.page(paginator.num_pages)
    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']   
        
    # Get available locations for autocomplete
    #available_locations = dumps([{'label':area.label, 'value':area.pk} for area in Area.objects.all().order_by('label')])
    
    #rdict = {'exchanges': exchanges, 'base_url': base_url, 'form': form, 'center': center_map, 'more_criteria': more_criteria, 'available_locations': available_locations, "search_form_template": search_form_template, "mode": mode, 'media_path': settings.MEDIA_URL, 'is_exchange': is_exchange}
    rdict = {'items': items_page, 'search_form_template': search_form_template, 'base_url': base_url, 'form': form}
    
    return rdict
                       




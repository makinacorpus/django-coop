# -*- coding: utf-8 -*-

from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from coop_local.models import Location

from django.conf import settings

from django.shortcuts import get_object_or_404

from ionyweb.website.rendering.medias import CSSMedia
from datetime import datetime

from .forms import PageApp_CoopServiceForm

from django.db.models import Q

from django.contrib.gis import geos
from coop_local.models import Organization, Offer, Exchange
from math import pi
from django.utils.simplejson import dumps

from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.core.mail import send_mail

MEDIAS = (
    CSSMedia('page_coop_service.css'),
)

def index_view(request, page_app):
    rdict = filter_data(request, page_app, "list")
    return render_view('page_coop_service/index.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))                           


def carto_view(request, page_app):
    rdict = filter_data(request, page_app, "carto")    
    return render_view('page_coop_service/index_carto.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request)) 


def filter_data(request, page_app, mode):
    base_url = u'%s' % (page_app.get_absolute_url())

    items = []
    
    # List all exchanges linked to a structure
    exchanges = Exchange.objects.filter(active=True, organization__isnull=False).order_by("title")

    # List all offer and services proposed by structures
    #offers = []
    #organizations = Organization.objects.filter(active=True).order_by("title")
    offers = Offer.objects.filter(provider__active=True).order_by("title")
    #for org in organizations:
        #for o in org.offer_set.all(): 
            #offers.append(o)

    search_form_template = "page_coop_service/search_form_service.html"
    
    if request.method == 'GET':  
        form = PageApp_CoopServiceForm(request.GET)
        more_criteria = False
        if form.is_valid():
            if form.cleaned_data['activity'] or form.cleaned_data['activity2']:
                exchanges = exchanges.filter(Q(activity=form.cleaned_data['activity']) | Q(activity=form.cleaned_data['activity2']))
                offers = offers.filter(Q(activity=form.cleaned_data['activity']) | Q(activity=form.cleaned_data['activity2']))

            if form.cleaned_data['location']:
                label = form.cleaned_data['location']
                pk = form.cleaned_data['location_id']
                area = get_object_or_404(Area, pk=pk)
                radius = form.cleaned_data['location_buffer']
                distance_degrees = (360 * radius) / (pi * 6378)
                zone = area.polygon.buffer(distance_degrees)
                ## Get the possible location in the buffer...
                possible_locations = Location.objects.filter(point__intersects=zone)
                # ...and filter organization according to these locations
                exchanges = exchanges.filter(Q(location__in=possible_locations))
                offers = offers.filter(Q(provider__location__in=possible_locations))
                
            if form.cleaned_data['thematic'] or form.cleaned_data['thematic2']:
                exchanges = exchanges.filter(Q(transverse_themes=form.cleaned_data['thematic']) | Q(transverse_themes=form.cleaned_data['thematic2']))
                offers = offers.filter(Q(provider__transverse_themes=form.cleaned_data['thematic']) | Q(provider__transverse_themes=form.cleaned_data['thematic2']))
                
            if form.cleaned_data['free_search']:
                exchanges = exchanges.filter(Q(title__contains=form.cleaned_data['free_search']) | Q(description__contains=form.cleaned_data['free_search']))
                offers = offers.filter(Q(title__contains=form.cleaned_data['free_search']) | Q(description__contains=form.cleaned_data['free_search']))
            
            if form.cleaned_data['method']:
                print exchanges
                exchanges = exchanges.filter(Q(methods__in=form.cleaned_data['method']))
                offers = [] # offers are not concern by mode, so we remove them from the selection
                
    else:
        form = PageApp_CoopServiceForm({'location_buffer': '10'}) # An empty form
        more_criteria = False
    
    center_map = settings.COOP_MAP_DEFAULT_CENTER
    
    # Get available locations for autocomplete
    #available_locations = dumps([{'label':area.label, 'value':area.pk} for area in Area.objects.all().order_by('label')])

    
    # Put all objects ina a common tab for pagination
    for e in exchanges :
        items.append({'type':'exchange', 'obj': e})

    for o in offers :
        items.append({'type':'offer', 'obj': o})

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
    
    rdict = {'items': items_page, 'search_form_template': search_form_template, 'base_url': base_url, 'exchanges_url': page_app.exchanges_url, 'organizations_url': page_app.organizations_url,'form': form, 'more_criteria': more_criteria}
    #rdict = {'exchanges': exchanges, 'base_url': base_url, 'form': form, 'center': center_map, 'more_criteria': more_criteria, 'available_locations': available_locations, "search_form_template": search_form_template, "mode": mode, 'media_path': settings.MEDIA_URL, 'is_exchange': is_exchange}

    
    return rdict
                       




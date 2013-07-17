# -*- coding: utf-8 -*-

from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from coop_local.models import Location

from django.conf import settings

from django.shortcuts import get_object_or_404

from ionyweb.website.rendering.medias import CSSMedia
from datetime import datetime

from .forms import PageApp_CoopTerritoryForm, CONTENT_TYPES

from django.db.models import Q

from django.contrib.gis import geos
from coop_local.models import Location, Area, Document, Exchange, Offer, Occurrence, Calendar, Organization
from math import pi
from django.utils.simplejson import dumps
from ionyweb_plugins.page_coop_blog.models import CoopEntry

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

    items = []
    
    # List all exchanges
    exchanges = Exchange.objects.filter(active=True).order_by("title")
    
    # List all events
    agenda = get_object_or_404(Calendar, sites__id=settings.SITE_ID)
    occ = Occurrence.objects.filter(
                        end_time__gt=datetime.now(),
                        event__active=True,
                        event__calendar=agenda,
                        ).order_by("start_time")
    
    # List all services
    services = Offer.objects.filter(provider__active=True).order_by("title")
    
    # List all organizations
    organizations = Organization.objects.filter(active=True, is_project=False).order_by("title")
    
    # List all projects
    projects = Organization.objects.filter(active=True, is_project=True).order_by("title")

    search_form_template = "page_coop_territory/search_form_territory.html"
    reset_exchanges = False
    reset_occ = False
    reset_services = False
    reset_organizations = False
    reset_projects = False
        
    if request.method == 'GET':  
        form = PageApp_CoopTerritoryForm(request.GET)
        more_criteria = False
        if form.is_valid():
            
            if form.cleaned_data['type_content']:
                reset_exchanges = True
                reset_occ = True
                reset_services = True
                reset_organizations = True
                reset_projects = True
                for c in form.cleaned_data['type_content']:
                    if c == '1':
                        reset_exchanges = False
                    if c == '2':
                        reset_occ = False
                    if c == '3':
                        reset_organizations = False
                    if c == '4':
                        reset_projects = False
                    if c == '5':
                        reset_services = False

            if form.cleaned_data['location']:
                label = form.cleaned_data['location']
                pk = form.cleaned_data['location_id']
                area = get_object_or_404(Area, pk=pk)
                radius = form.cleaned_data['location_buffer']
                distance_degrees = (360 * radius) / (pi * 6378)
                zone = area.polygon.buffer(distance_degrees)
                ### Get the possible location in the buffer...
                possible_locations = Location.objects.filter(point__intersects=zone)
                ## ...and filter according to these locations
                exchanges = exchanges.filter(Q(location__in=possible_locations))
                occ = occ.filter(Q(event__location__in=possible_locations))
                # TODO services = 
                organizations = organizations.filter(Q(located__location__in=possible_locations))
                projects = projects.filter(Q(located__location__in=possible_locations))

                
            #if form.cleaned_data['activity'] or form.cleaned_data['activity2']:
                #exchanges = exchanges.filter(Q(activity=form.cleaned_data['activity']) | Q(activity=form.cleaned_data['activity2']))
            if form.cleaned_data['activity'] and form.cleaned_data['activity2']:
                activity = form.cleaned_data['activity']
                activity2 = form.cleaned_data['activity2']
                
                tab_keep = get_list_org_to_keep(organizations, activity)
                tab_keep2 = get_list_org_to_keep(organizations, activity2)
                organizations = organizations.filter(Q(pk__in=tab_keep) | Q(pk__in=tab_keep2) )
                #TODO occ
                #TODO exchanges
                #TODO services
                #TODO projects
            else:
                if form.cleaned_data['activity']:
                    activity = form.cleaned_data['activity']                    
                    tab_keep = get_list_org_to_keep(organizations, activity)
                    organizations = organizations.filter(pk__in=tab_keep)
                else:
                    if form.cleaned_data['activity2']:
                        activity = form.cleaned_data['activity2']                    
                        tab_keep = get_list_org_to_keep(organizations, activity)
                        organizations = organizations.filter(pk__in=tab_keep)                
                
            if form.cleaned_data['thematic'] or form.cleaned_data['thematic2']:
                arg = Q()
                if form.cleaned_data['thematic']: 
                    arg = Q(transverse_themes=form.cleaned_data['thematic'])
                if form.cleaned_data['thematic2']: 
                    arg = arg | Q(transverse_themes=form.cleaned_data['thematic2'])
                exchanges = exchanges.filter(arg)
                organizations = organizations.filter(arg)
                projects = projects.filter(arg)
                #TODO occ
                #TODO services
                
                
            if form.cleaned_data['free_search']:
                exchanges = exchanges.filter(Q(title__contains=form.cleaned_data['free_search']) | Q(description__contains=form.cleaned_data['free_search']))
                #TODO occ
                #TODO services
                #TODO organization
                #TODO projects


            if form.cleaned_data['statut'] or form.cleaned_data['statut2']:
                # we clear all except organizations
                exchanges = None
                occ = None
                services = None
                
                arg = Q()
                if form.cleaned_data['statut']:
                    arg = Q(legal_status=form.cleaned_data['statut'])
                if form.cleaned_data['statut2']:
                    arg = arg | Q(legal_status=form.cleaned_data['statut2'])
                organizations = organizations.filter(arg)
                projects = projects.filter(arg)            
            
    else:
        form = PageApp_CoopTerritoryForm({'location_buffer': '10'}) # An empty form
        more_criteria = False
    
    center_map = settings.COOP_MAP_DEFAULT_CENTER
    
    # Get available locations for autocomplete
    available_locations = dumps([{'label':area.label, 'value':area.pk} for area in Area.objects.all().order_by('label')])


    # If a filter on content_type has been set, reset
    if reset_exchanges:
        exchanges = None
    if reset_occ:
        occ = None
    if reset_services:
        services = None
    if reset_organizations:
        organizations = None
    if reset_projects:
        projects = None
    
    # Put all objects ina a common tab for pagination
    if exchanges:
        for e in exchanges :
            items.append({'type':'exchange', 'obj': e})
    if occ:
        for o in occ :
            items.append({'type':'occ', 'obj': o})
    if services:
        for s in services :
            items.append({'type':'service', 'obj': s})
    if organizations:
        for o in organizations :
            items.append({'type':'organization', 'obj': o})
    if projects:
        for o in projects :
            items.append({'type':'project', 'obj': o})
        
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
    
    rdict = {'items': items_page, 'search_form_template': search_form_template, 'base_url': base_url, 'exchanges_url': page_app.exchanges_url, 'organizations_url': page_app.organizations_url, 'projects_url': page_app.projects_url, 'agenda_url': page_app.agenda_url, 'blog_url': page_app.blog_url, 'form': form, 'more_criteria': more_criteria, 'available_locations': available_locations}
    
    return rdict

    
def get_list_org_to_keep(organizations, activity):    
    tab_keep = []
    for org in organizations:
        for o in org.offer_set.all():
            parent = get_parent_activity_leve_0(o.activity)
            if parent == activity.label:
                tab_keep.append(org.pk)
    return tab_keep
    
def get_parent_activity_leve_0(activity):
    if activity.parent:
        return get_parent_activity_leve_0(activity.parent)
    else:
        return activity.label   

# -*- coding: utf-8 -*-

from math import pi

from django.template import RequestContext
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.gis import geos
from django.utils.simplejson import dumps
from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.mail import send_mail

from ionyweb_plugins.page_coop_blog.models import CoopEntry
from ionyweb.website.rendering.medias import CSSMedia
from ionyweb.website.rendering.utils import render_view
from datetime import datetime

from .forms import PageApp_CoopSearchGlobalForm, CONTENT_TYPES

from coop_local.models import Location, Area, Document, Exchange, Offer, Occurrence, Calendar, Organization


MEDIAS = (
    CSSMedia('page_coop_searchglobal.css'),
)

"""
This page_app works with both 'plugin_coop_searchglobal' AND 'plugin_coop_tagcloud'.
The two plugins send a GET search_string or search_string_tag for a search in the DB objects
"""

def index_view(request, page_app):
    rdict = filter_data(request, page_app, "list")
    return render_view('page_coop_searchglobal/index.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))                           


def filter_data(request, page_app, mode):
    base_url = u'%s' % (page_app.get_absolute_url())

    items = []
    
    # List all exchanges
    exchanges = None
    if 'exchanges' in settings.COOP_SEARCHGLOBAL_THEMES:
        exchanges = Exchange.objects.filter(active=True).order_by("-modified")
    
    # List all events
    if 'agenda' in settings.COOP_SEARCHGLOBAL_THEMES:
        agenda = get_object_or_404(Calendar, sites__id=settings.SITE_ID)
        occ = Occurrence.objects.filter(
                        end_time__gt=datetime.now(),
                        event__active=True,
                        event__calendar=agenda,
                        ).order_by("start_time")
    
    # List all services
    services = None
    if 'services' in settings.COOP_SEARCHGLOBAL_THEMES:
        services = Offer.objects.filter(provider__active=True).order_by("title")
    
    # List all organizations
    organizations = None
    if 'organizations' in settings.COOP_SEARCHGLOBAL_THEMES:
        organizations = Organization.objects.filter(active=True, is_project=False).order_by("-modified")
    
    # List all projects
    projects = None
    if 'projects' in settings.COOP_SEARCHGLOBAL_THEMES:
        projects = Organization.objects.filter(active=True, is_project=True).order_by("-modified")

    # List all offers
    offers = None
    if 'offers' in settings.COOP_SEARCHGLOBAL_THEMES:
        offers = Offer.objects.filter(provider__active=True).order_by("-modified")

    # List all articles
    entries = None
    if 'articles' in settings.COOP_SEARCHGLOBAL_THEMES:
        entries = CoopEntry.objects.filter(status=1).order_by('-modification_date')

    if request.method == 'GET':  
        if 'search_string' in request.GET:
            search_string = request.GET['search_string']
            if search_string is not None and search_string != '':

                if 'agenda' in settings.COOP_SEARCHGLOBAL_THEMES:
                    occ = occ.filter(Q(event__title__icontains=search_string) \
                                    |Q(event__description__icontains=search_string) \
                                    |Q(event__tagged_items__tag__name__in=[search_string]) \
                                    |Q(event__activity__label__icontains=search_string) \
                                    |Q(event__transverse_themes__name__icontains=search_string) \
                                    |Q(event__organization__title__icontains=search_string) \
                                    |Q(event__location__city__icontains=search_string) \
                                    ).distinct()

                if 'organizations' in settings.COOP_SEARCHGLOBAL_THEMES:
                    organizations = organizations.filter(Q(title__icontains=search_string) \
                                                        |Q(description__icontains=search_string) \
                                                        |Q(short_description__icontains=search_string) \
                                                        |Q(tagged_items__tag__name__in=[search_string]) \
                                                        |Q(offer__activity__label__icontains=search_string) \
                                                        |Q(transverse_themes__name__icontains=search_string) \
                                                        ).distinct()
                
                if 'articles' in settings.COOP_SEARCHGLOBAL_THEMES:
                    entries = entries.filter(Q(title__icontains=search_string) \
                                            |Q(resume__icontains=search_string) \
                                            |Q(body__icontains=search_string) \
                                            |Q(tagged_items__tag__name__in=[search_string]) \
                                            |Q(activity__label__icontains=search_string) \
                                            |Q(transverse_themes__name__icontains=search_string) \
                                            ).distinct()

                # TODO : extra searches for PES (services, projects...)
                #if 'services' in settings.COOP_SEARCHGLOBAL_THEMES:
                #if 'exchanges' in settings.COOP_SEARCHGLOBAL_THEMES:
                #if 'projects' in settings.COOP_SEARCHGLOBAL_THEMES:
                #if 'offers' in settings.COOP_SEARCHGLOBAL_THEMES:

        if 'search_string_tag' in request.GET:
            search_string_tag = request.GET['search_string_tag']
            if search_string_tag is not None and search_string_tag != '':

                if 'agenda' in settings.COOP_SEARCHGLOBAL_THEMES:
                    occ = occ.filter(event__tagged_items__tag__name__in=[search_string_tag])
                    
                if 'organizations' in settings.COOP_SEARCHGLOBAL_THEMES:
                    organizations = organizations.filter(tagged_items__tag__name__in=[search_string_tag])
                    
                if 'articles' in settings.COOP_SEARCHGLOBAL_THEMES:
                    entries = entries.filter(tagged_items__tag__name__in=[search_string_tag])

                # TODO : extra searches for PES (services, projects...)
                #if 'services' in settings.COOP_SEARCHGLOBAL_THEMES:
                #if 'exchanges' in settings.COOP_SEARCHGLOBAL_THEMES:
                #if 'projects' in settings.COOP_SEARCHGLOBAL_THEMES:
                #if 'offers' in settings.COOP_SEARCHGLOBAL_THEMES:
    
    
    # Put all objects in a a common tab for pagination
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
    if entries:
        for e in entries :
            items.append({'type':'entrie', 'obj': e})
        
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
    
    rdict = {'items': items_page, 'base_url': base_url, 'exchanges_url': page_app.exchanges_url, 'organizations_url': page_app.organizations_url, 'projects_url': page_app.projects_url, 'agenda_url': page_app.agenda_url, 'blog_url': page_app.blog_url, 'media_path': settings.MEDIA_URL, 'get_params': get_params.urlencode()}
    
    return rdict

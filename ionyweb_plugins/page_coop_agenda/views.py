# -*- coding: utf-8 -*-

from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from coop_local.models import Event, EventCategory, Calendar, Occurrence
from django.conf import settings

from django.shortcuts import get_object_or_404

from ionyweb.website.rendering.medias import CSSMedia
from datetime import datetime

from .forms import PageApp_CoopAgendaForm, PartialEventForm

from django.db.models import Q

from django.contrib.gis import geos
from django.contrib.gis.measure import D
from coop_local.models import Location
from django.utils.simplejson import dumps

from math import pi

MEDIAS = (
    CSSMedia('page_coop_agenda.css'),
    )

def index_view(request, page_app):
    rdict = filter_data(request, page_app)
    return render_view('page_coop_agenda/index.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))                           


def carto_view(request, page_app):
    rdict = filter_data(request, page_app)    
    return render_view('page_coop_agenda/index_carto.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request))     
    
def filter_data(request, page_app):
    
    base_url = u'%s' % (page_app.get_absolute_url())

    agenda = get_object_or_404(Calendar, sites__id=settings.SITE_ID)
    categories = {}

    center_map = settings.COOP_MAP_DEFAULT_CENTER
    
    search_form_template = "page_coop_agenda/search_form_agenda.html"
    
    try:
        search_form = settings.COOP_AGENDA_SEARCH_FORM
    except:
        search_form = False
    
    occs_count = 0
    for cat in EventCategory.objects.all():
        occ = Occurrence.objects.filter(
                            end_time__gt=datetime.now(),
                            event__active=True,
                            event__calendar=agenda,
                            event__category=cat
                            ).order_by("start_time")
        if occ.exists():
            categories[cat] = occ
            occs_count += occ.count()
                            
 
    if search_form:
        if request.method == 'POST': # If the form has been submitted
            occs_count = 0
            categories = {}
            form = PageApp_CoopAgendaForm(request.POST)
            if form.is_valid():
                for cat in EventCategory.objects.all():
                    occ = Occurrence.objects.filter(
                                        #end_time__gt=datetime.now(),
                                        event__active=True,
                                        event__calendar=agenda,
                                        event__category=cat
                                        ).order_by("start_time")

                    if occ.exists() and form.cleaned_data['free_search']:
                        occ = occ.filter(Q(event__title__contains=form.cleaned_data['free_search']) | Q(event__description__contains=form.cleaned_data['free_search']))

                    if occ.exists() and form.cleaned_data['location']:
                        label = form.cleaned_data['location']
                        location = get_object_or_404(Location, label=label)                
                        center = geos.Point(float(location.point.x), float(location.point.y))
                        radius = form.cleaned_data['location_buffer']
                        distance_degrees = (360 * radius) / (pi * 6378)
                        zone = center.buffer(distance_degrees)
                        
                        # Get the possible location in the buffer...
                        possible_locations = Location.objects.filter(point__intersects=zone)
                        # ...and filter events according to these locations
                        occ = occ.filter(Q(event__location__in=possible_locations))

                        
                    if occ.exists() and form.cleaned_data['organization']:
                        occ = occ.filter(Q(event__organization__in=form.cleaned_data['organization']))

                    if occ.exists() and form.cleaned_data['type']:
                        occ = occ.filter(Q(event__event_type__in=form.cleaned_data['type']))

                    if occ.exists() and form.cleaned_data['start_date']:
                        occ = occ.filter(Q(start_time__gt=form.cleaned_data['start_date']))

                    if occ.exists() and form.cleaned_data['end_date']:
                        occ = occ.filter(Q(end_time__lt=form.cleaned_data['end_date']))
                        
                    # TODO filter activity
                    
                    if occ.exists():
                        categories[cat] = occ
                        occs_count += occ.count()
        else:
            form = PageApp_CoopAgendaForm(initial={'location_buffer': '10'}) # An empty form
    
    # Get available locations for autocomplete
    available_locations = dumps([location.label for location in Location.objects.all()])
 
    rdict = {'agenda': agenda, 'events_by_categories': categories, 'object': page_app, 'base_url': base_url, 'search_form': search_form, 'form': form, 'center': center_map, 'occs_count': occs_count, 'available_locations': available_locations, 'search_form_template': search_form_template}
    
    return rdict


def detail_view(request, page_app, pk):
    event = get_object_or_404(Event, pk=pk)
    base_url = u'%sp/' % (page_app.get_absolute_url())
    rdict = {'object': page_app, 'e': event, 'media_path': settings.MEDIA_URL, 'base_url': base_url}
    return render_view('page_coop_agenda/detail.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))                              


def add_view(request, page_app, event_id=None):
    if request.user.is_authenticated():
        center_map = settings.COOP_MAP_DEFAULT_CENTER

        if event_id:
            # update
            mode = 'update'
            event = get_object_or_404(Event, pk=event_id)
            base_url = u'%sp/event_edit/%s' % (page_app.get_absolute_url(),event_id)

        else :
            # new
            mode = 'add'
            base_url = u'%sp/event_add' % (page_app.get_absolute_url())
            event = Event()
        
        
        if request.method == 'POST': # If the form has been submitted        
            form = PartialEventForm(request.POST, instance = event)
            
            if form.is_valid():
                event = form.save()
                base_url = u'%s' % (page_app.get_absolute_url())
                rdict = {'base_url': base_url}
                return render_view('page_coop_agenda/add_success.html',
                                rdict,
                                MEDIAS,
                                context_instance=RequestContext(request))
        else:
            form = PartialEventForm(instance=event) # An empty form
        
        rdict = {'media_path': settings.MEDIA_URL, 'base_url': base_url, 'form': form, 'center': center_map, 'mode': mode}
        return render_view('page_coop_agenda/add.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request))
    else:
        return render_view('page_coop_agenda/forbidden.html')


                       
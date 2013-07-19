# -*- coding: utf-8 -*-

from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from coop_local.models import Event, EventCategory, Calendar, Occurrence, Document
from django.conf import settings

from django.shortcuts import get_object_or_404

from ionyweb.website.rendering.medias import CSSMedia
from datetime import datetime
from coop.org.models import get_rights

from .forms import PageApp_CoopAgendaForm, PartialEventForm, PartialOccEventForm, DocumentForm, ReplyEventForm
from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.forms.models import inlineformset_factory, formset_factory
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.db.models import Q

from django.contrib.gis import geos
from django.contrib.gis.measure import D
from coop_local.models import Location, Area
from coop.base_models import Located

from django.utils.simplejson import dumps

from math import pi

MEDIAS = (
    CSSMedia('page_coop_agenda.css'),
    )

def index_view(request, page_app):
    rdict = filter_data(request, page_app, "list")
    return render_view('page_coop_agenda/index.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))                           


def carto_view(request, page_app):
    rdict = filter_data(request, page_app, "carto")    
    return render_view('page_coop_agenda/index_carto.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request))     
    
def filter_data(request, page_app, mode):
    
    base_url = u'%s' % (page_app.get_absolute_url())

    agenda = get_object_or_404(Calendar, sites__id=settings.SITE_ID)

    center_map = settings.COOP_MAP_DEFAULT_CENTER
    
    search_form_template = "page_coop_agenda/search_form_agenda.html"
    
    try:
        search_form = settings.COOP_AGENDA_SEARCH_FORM
    except:
        search_form = False
    
    occ = Occurrence.objects.filter(
                        end_time__gt=datetime.now(),
                        event__active=True,
                        event__calendar=agenda,
                        ).order_by("start_time")
 
    more_criteria = False
    
    if search_form:
        if request.method == 'GET': # If the form has been submitted
            form = PageApp_CoopAgendaForm(request.GET)
            if form.is_valid():

                occ = Occurrence.objects.filter(
                                    event__active=True,
                                    event__calendar=agenda,
                                    ).order_by("start_time")
                if occ.exists() and form.cleaned_data['free_search']:
                    occ = occ.filter(Q(event__title__contains=form.cleaned_data['free_search']) | Q(event__description__contains=form.cleaned_data['free_search']))

                if occ.exists() and form.cleaned_data['location']:
                    label = form.cleaned_data['location']
                    pk = form.cleaned_data['location_id']
                    area = get_object_or_404(Area, pk=pk)
                    radius = form.cleaned_data['location_buffer']
                    distance_degrees = (360 * radius) / (pi * 6378)
                    zone = area.polygon.buffer(distance_degrees)
                    # Get the possible location in the buffer...
                    possible_locations = Location.objects.filter(point__intersects=zone)
                    # ...and filter occ according to these locations
                    occ = occ.filter(Q(event__location__in=possible_locations))

                    
                if occ.exists() and form.cleaned_data['organization']:
                    occ = occ.filter(Q(event__organization__in=form.cleaned_data['organization']))

                if occ.exists() and form.cleaned_data['type']:
                    occ = occ.filter(Q(event__event_type__in=form.cleaned_data['type']))

                if occ.exists() and form.cleaned_data['start_date']:
                    occ = occ.filter(Q(start_time__gt=form.cleaned_data['start_date']))

                if occ.exists() and form.cleaned_data['end_date']:
                    occ = occ.filter(Q(end_time__lt=form.cleaned_data['end_date']))
                    
                if form.cleaned_data['thematic'] or form.cleaned_data['thematic2']:
                    arg = Q()
                    if form.cleaned_data['thematic']: 
                        arg = Q(event__transverse_themes=form.cleaned_data['thematic'])
                    if form.cleaned_data['thematic2']: 
                        arg = arg | Q(event__transverse_themes=form.cleaned_data['thematic2'])
                    occ = occ.filter(arg)
                
                    
                if form.cleaned_data['activity'] and form.cleaned_data['activity2']:
                    activity = form.cleaned_data['activity']
                    activity2 = form.cleaned_data['activity2']
                    
                    tab_keep = get_list_event_to_keep(occ, activity)
                    tab_keep2 = get_list_event_to_keep(occ, activity2)
                    occ = occ.filter(Q(pk__in=tab_keep) | Q(pk__in=tab_keep2) )

                else:
                    if form.cleaned_data['activity']:
                        activity = form.cleaned_data['activity']                    
                        tab_keep = get_list_event_to_keep(occ, activity)
                        occ = occ.filter(pk__in=tab_keep)
                    else:
                        if form.cleaned_data['activity2']:
                            activity = form.cleaned_data['activity2']                    
                            tab_keep = get_list_event_to_keep(occ, activity)
                            occ = occ.filter(pk__in=tab_keep)                    

                if request.GET.get('more_criteria_status'):
                    if request.GET['more_criteria_status'] == 'True':
                        more_criteria = True

                            
        else:
            form = PageApp_CoopAgendaForm(initial={'location_buffer': '10'}) # An empty form
            more_criteria = False
    
    paginator = Paginator(occ, 10)
    page = request.GET.get('page')
    try:
        occ_page = paginator.page(page)
    except PageNotAnInteger:
        occ_page = paginator.page(1)
    except EmptyPage:
        occ_page = paginator.page(paginator.num_pages)
    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']      
    
    # Get available locations for autocomplete
    available_locations = dumps([{'label':area.label, 'value':area.pk} for area in Area.objects.all().order_by('label')])
 
    rdict = {'media_path': settings.MEDIA_URL,'agenda': agenda, 'occs': occ_page, 'object': page_app, 'base_url': base_url, 'search_form': search_form, 'form': form, 'center': center_map, 'available_locations': available_locations, 'search_form_template': search_form_template, "mode": mode, 'more_criteria' : more_criteria}
    
    return rdict


    
def get_list_event_to_keep(occs, activity):    
    tab_keep = []
    for o in occs:
        if o.event.activity:
            parent = get_parent_activity_leve_0(o.event.activity)
            if parent == activity.label:
                tab_keep.append(o.pk)
    return tab_keep

def get_parent_activity_leve_0(activity):
    if activity.parent:
        return get_parent_activity_leve_0(activity.parent)
    else:
        return activity.label
        
        
# this function is for promess84 compatibility :
"""
def filter_data_with_cat (request, page_app, mode):
    
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
                    occ = Occurrence.objec    ts.filter(
                                        #end_time__gt=datetime.now(),
                                        event__active=True,
                                        event__calendar=agenda,
                                        event__category=cat
                                        ).order_by("start_time")
                    if occ.exists() and form.cleaned_data['free_search']:
                        occ = occ.filter(Q(event__title__contains=form.cleaned_data['free_search']) | Q(event__description__contains=form.cleaned_data['free_search']))

                    if occ.exists() and form.cleaned_data['location']:
                        label = form.cleaned_data['location']
                        pk = form.cleaned_data['location_id']
                        area = get_object_or_404(Area, pk=pk)
                        radius = form.cleaned_data['location_buffer']
                        distance_degrees = (360 * radius) / (pi * 6378)
                        zone = area.polygon.buffer(distance_degrees)
                        # Get the possible location in the buffer...
                        possible_locations = Location.objects.filter(point__intersects=zone)
                        # ...and filter occ according to these locations
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
                    if form.cleaned_data['thematic'] or form.cleaned_data['thematic2']:
                        occ = occ.filter(Q(event__transverse_themes=form.cleaned_data['thematic']) | Q(event__transverse_themes=form.cleaned_data['thematic2']))
                    
                    if form.cleaned_data['activity'] or form.cleaned_data['activity2']:
                        occ = occ.filter(Q(event__activity=form.cleaned_data['activity']) | Q(event__activity=form.cleaned_data['activity2']))
                    
                    if occ.exists():
                        categories[cat] = occ
                        occs_count += occ.count()
        else:
            form = PageApp_CoopAgendaForm(initial={'location_buffer': '10'}) # An empty form
        
    # Get available locations for autocomplete
    available_locations = dumps([{'label':area.label, 'value':area.pk} for area in Area.objects.all().order_by('label')])
 
    rdict = {'media_path': settings.MEDIA_URL,'agenda': agenda, 'events_by_categories': categories, 'object': page_app, 'base_url': base_url, 'search_form': search_form, 'form': form, 'center': center_map, 'occs_count': occs_count, 'available_locations': available_locations, 'search_form_template': search_form_template, "mode": mode}
    
    return rdict    
"""

def detail_view(request, page_app, pk):
    event = get_object_or_404(Event, pk=pk)
    base_url = u'%sp/' % (page_app.get_absolute_url())
    imgs = event.document_set.filter(type__name='Galerie')
    docs = event.document_set.exclude(type__name='Galerie')
    rdict = {'object': page_app, 'e': event, 'media_path': settings.MEDIA_URL, 'base_url': base_url, 'imgs': imgs, 'docs': docs}
    return render_view('page_coop_agenda/detail.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))                              


def add_view(request, page_app, event_id=None):
    event_form_class = PartialEventForm
    occ_form_class = PartialOccEventForm
    agenda = get_object_or_404(Calendar, sites__id=settings.SITE_ID)                
    
    if request.user.is_authenticated():
        center_map = settings.COOP_MAP_DEFAULT_CENTER
        DocFormSet = generic_inlineformset_factory(Document, form=DocumentForm, extra=1)
        #OccFormSet = inlineformset_factory(Event, Occurrence, form=PartialOccEventForm, extra=1)

        if event_id:
            # update
            mode = 'update'
            event = get_object_or_404(Event, pk=event_id)
            occ = get_object_or_404(Occurrence, event__pk = event_id)
            base_url = u'%sp/event_edit/%s' % (page_app.get_absolute_url(),event_id)
            delete_url = u'%sp/event_delete/%s' % (page_app.get_absolute_url(),event_id)
        else :
            # new
            mode = 'add'
            base_url = u'%sp/event_add' % (page_app.get_absolute_url())
            delete_url = ''
            event = Event(calendar=agenda)
            occ = Occurrence(event=event)

        if request.method == 'POST':
            
            event_form = event_form_class(request.POST, request.FILES, instance = event)
            docFormset = DocFormSet(request.POST, request.FILES, prefix='doc', instance=event)
            occ_form = occ_form_class(request.POST, instance = occ)
            #occFormset = OccFormSet(request.POST, request.FILES, prefix='occ', instance=event)
            
            if event_form.is_valid() and occ_form.is_valid() and docFormset.is_valid():
                event = event_form.save()
                event_form.save_m2m()
                docFormset.save()
                occ.event_id = event.pk
                occ = occ_form.save(event)
                
                                
                base_url = u'%s' % (page_app.get_absolute_url())
                rdict = {'base_url': base_url, 'event_id': occ.event_id}
                return render_view('page_coop_agenda/add_success.html',
                                rdict,
                                MEDIAS,
                                context_instance=RequestContext(request))

        else:
            event_form = event_form_class(instance = event)
            occ_form = occ_form_class(instance = occ)
            docFormset = DocFormSet(prefix='doc', instance=event)
            #occFormset = OccFormSet(prefix='occ', instance=event)
        
        rdict = {'media_path': settings.MEDIA_URL, 'base_url': base_url, 'delete_url': delete_url, 'form': event_form, 'doc_form': docFormset, 'occ_form': occ_form, 'center': center_map, 'mode': mode}
        return render_view('page_coop_agenda/add.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request))
    else:
        return render_view('page_coop_agenda/forbidden.html')


def reply_view(request, page_app, event_id=None):
    if request.user.is_authenticated():
        base_url = u'%sp/event_reply/%s' % (page_app.get_absolute_url(),event_id)
        if request.method == 'POST': # If the form has been submitted        
            form = ReplyEventForm(request.POST)
            
            if form.is_valid():
                title = form.cleaned_data['title']
                response = form.cleaned_data['response']
                email = form.cleaned_data['email']
                
                try:
                    event = Event.objects.get(pk=event_id)
                except Area.DoesNotExist:
                    event = None
                
                send_ok = False
                if event and event.organization:
                    if event.organization.pref_email:
                        try :
                            # send email
                            send_mail(title, response, email, [event.organization.pref_email.content ], fail_silently=False)
                            send_ok = True
                        except:
                            pass
                
                template = "page_coop_agenda/reply_success.html"
                if not send_ok:
                    template = "page_coop_agenda/reply_fail.html"

                base_url = u'%s' % (page_app.get_absolute_url())
                rdict = {'base_url': base_url, 'event_id': event.id}
                return render_view(template,
                            rdict,
                            MEDIAS,
                            context_instance=RequestContext(request))
                
        else:
            form = ReplyEventForm() # An empty form
        
        rdict = {'media_path': settings.MEDIA_URL, 'base_url': base_url, 'form': form}
        return render_view('page_coop_agenda/reply.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request))
    else:
        return render_view('page_coop_agenda/forbidden.html')


def delete_view(request, page_app, event_id):
    # check rights    
    can_edit, can_add = get_rights(request, Event.objects.get(pk=event_id).organization.pk)
    if can_edit :
        u = Event.objects.get(pk=event_id).delete()
        base_url = u'%s' % (page_app.get_absolute_url())
        rdict = {'base_url': base_url}
        return render_view('page_coop_agenda/delete_success.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request))
    else:
        return render_view('page_coop_agenda/forbidden.html')
        
        
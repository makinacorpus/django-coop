# -*- coding: utf-8 -*-

from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from coop_local.models import Organization
from django.conf import settings

from django.shortcuts import get_object_or_404

from ionyweb.website.rendering.medias import CSSMedia

from .forms import PageApp_MembersForm, PartialMemberForm

from django.db.models import Q

from django.contrib.gis import geos
from coop_local.models import Location
from django.utils.simplejson import dumps

from math import pi


MEDIAS = (
    CSSMedia('page_members.css'),
    )

def index_view(request, page_app):    
    rdict = filter_data(request, page_app)
    return render_view('page_members/index.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))                           


def carto_view(request, page_app):
    rdict = filter_data(request, page_app)    
    return render_view('page_members/index_carto.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request)) 

def filter_data(request, page_app):
    if page_app.type != "":
        organizations = Organization.objects.filter(category__label=page_app.type)
    else:
        organizations = Organization.objects.all()
            
    base_url = u'%s' % (page_app.get_absolute_url())
    
    direct_link = False
    if page_app.type == settings.COOP_PARTENAIRE_LABEL:
        direct_link = True
    
    try:
        search_form = settings.COOP_MEMBER_SEARCH_FORM
    except:
        search_form = False

    center_map = settings.COOP_MAP_DEFAULT_CENTER
        
    if request.method == 'POST': # If the form has been submitted
        form = PageApp_MembersForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['free_search']:
                organizations = organizations.filter(Q(title__contains=form.cleaned_data['free_search']) | Q(description__contains=form.cleaned_data['free_search']))

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
                organizations = organizations.filter(Q(located__location__in=possible_locations))

            if form.cleaned_data['thematic'] or form.cleaned_data['thematic2'] or form.cleaned_data['thematic3']:
                organizations = organizations.filter(Q(transverse_themes=form.cleaned_data['thematic']) | Q(transverse_themes=form.cleaned_data['thematic2']) | Q(transverse_themes=form.cleaned_data['thematic3']))
                
            if form.cleaned_data['activity'] or form.cleaned_data['activity2']:
                organizations = organizations.filter(Q(activity=form.cleaned_data['activity']) | Q(activity=form.cleaned_data['activity2']))

            if form.cleaned_data['statut']:
                organizations = organizations.filter(Q(statut=form.cleaned_data['statut']))
            
    else:
        form = PageApp_MembersForm(initial={'location_buffer': '10'}) # An empty form
    
    
    # Get available locations for autocomplete
    available_locations = dumps([location.label for location in Location.objects.all()])
    
    rdict = {'object': page_app, 'members': organizations, 'media_path': settings.MEDIA_URL, 'base_url': base_url, 'direct_link': direct_link, 'search_form': search_form, 'form' : form, 'center': center_map, 'available_locations': available_locations}

    return rdict
    
    
    
#def index_view(request, page_app):
    #if page_app.type != "":
        #organizations = Organization.objects.filter(category__label=page_app.type)
    #else:
        #organizations = Organization.objects.all()
            
    #base_url = u'%s' % (page_app.get_absolute_url())
    
    #direct_link = False
    #if page_app.type == settings.COOP_PARTENAIRE_LABEL:
        #direct_link = True
    
    #try:
        #search_form = settings.COOP_MEMBER_SEARCH_FORM
    #except:
        #search_form = False

    #center_map = settings.COOP_MAP_DEFAULT_CENTER
        
    #if request.method == 'POST': # If the form has been submitted
        #form = PageApp_MembersForm(request.POST)
        #if form.is_valid():
            #if form.cleaned_data['free_search']:
                #organizations = organizations.filter(Q(title__contains=form.cleaned_data['free_search']) | Q(description__contains=form.cleaned_data['free_search']))

            #if form.cleaned_data['location']:
                #label = form.cleaned_data['location']
                #location = get_object_or_404(Location, label=label)                
                #center = geos.Point(float(location.point.x), float(location.point.y))
                #radius = form.cleaned_data['location_buffer']
                #distance_degrees = (360 * radius) / (pi * 6378)
                #zone = center.buffer(distance_degrees)
                
                 ## Get the possible location in the buffer...
                #possible_locations = Location.objects.filter(point__intersects=zone)
                ## ...and filter organization according to these locations
                #organizations = organizations.filter(Q(located__location__in=possible_locations))

            #if form.cleaned_data['thematic'] or form.cleaned_data['thematic2'] or form.cleaned_data['thematic3']:
                #organizations = organizations.filter(Q(transverse_themes=form.cleaned_data['thematic']) | Q(transverse_themes=form.cleaned_data['thematic2']) | Q(transverse_themes=form.cleaned_data['thematic3']))
                
            #if form.cleaned_data['activity'] or form.cleaned_data['activity2']:
                #organizations = organizations.filter(Q(activity=form.cleaned_data['activity']) | Q(activity=form.cleaned_data['activity2']))

            #if form.cleaned_data['statut']:
                #organizations = organizations.filter(Q(statut=form.cleaned_data['statut']))
            
    #else:
        #form = PageApp_MembersForm(initial={'location_buffer': '10'}) # An empty form
    
    
    ## Get available locations for autocomplete
    #available_locations = dumps([location.label for location in Location.objects.all()])
    
    #rdict = {'object': page_app, 'members': organizations, 'media_path': settings.MEDIA_URL, 'base_url': base_url, 'direct_link': direct_link, 'search_form': search_form, 'form' : form, 'center': center_map, 'available_locations': available_locations}
    
    #return render_view('page_members/index.html',
                       #rdict,
                       #MEDIAS,
                       #context_instance=RequestContext(request))


def detail_view(request, page_app, pk):
    member = get_object_or_404(Organization, pk=pk)
    return render_view('page_members/detail.html',
                       { 'member':  member, 'media_path': settings.MEDIA_URL },
                       MEDIAS,
                       context_instance=RequestContext(request))
                       
def add_view(request, page_app):
    if request.user.is_authenticated():
        base_url = u'%sp/member_add' % (page_app.get_absolute_url())
        center_map = settings.COOP_MAP_DEFAULT_CENTER

        if request.method == 'POST': # If the form has been submitted        
            member = Organization()
            form = PartialMemberForm(request.POST, request.FILES, instance = member)
            
            if form.is_valid():
                member = form.save()
                base_url = u'%s' % (page_app.get_absolute_url())
                rdict = {'base_url': base_url}
                return render_view('page_members/add_success.html',
                                rdict,
                                MEDIAS,
                                context_instance=RequestContext(request))
        else:
            form = PartialMemberForm() # An empty form
        
        rdict = {'media_path': settings.MEDIA_URL, 'base_url': base_url, 'form': form, 'center': center_map}
        return render_view('page_members/add.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request))
    else:
        return render_view('page_members/forbidden.html')

        
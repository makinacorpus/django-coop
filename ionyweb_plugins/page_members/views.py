# -*- coding: utf-8 -*-

from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from coop_local.models import Organization
from django.conf import settings

from django.shortcuts import get_object_or_404

from ionyweb.website.rendering.medias import CSSMedia

from .forms import PageApp_MembersForm

from django.db.models import Q

from django.contrib.gis import geos
from coop_local.models import Location

MEDIAS = (
    CSSMedia('page_members.css'),
    )

def index_view(request, page_app):
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
        # TODO: other filters
        form = PageApp_MembersForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['free_search']:
                organizations = organizations.filter(Q(title__contains=form.cleaned_data['free_search']) | Q(description__contains=form.cleaned_data['free_search']))

            if form.cleaned_data['location']:
                coords = form.cleaned_data['location'].split(",")
                center = geos.Point(float(coords[0]), float(coords[1]))
                radius = form.cleaned_data['location_buffer']
                zone = center.buffer(float(radius))
                
                 # Get the possible location in the buffer...
                possible_locations = Location.objects.filter(point__intersects=zone)
                for o in Location.objects.all():
                    print o.point
                print possible_locations
                print zone
                # ...and filter organization according to these locations
                organizations = organizations.filter(Q(located__location__in=possible_locations))
            
            #if form.cleaned_data['type_exchange']:
            #    organizations = organizations.filter(Q(eway__in=form.cleaned_data['type_exchange']))

            #if form.cleaned_data['type']:
            #    organizations = organizations.filter(Q(etype__in=form.cleaned_data['type']))

    else:
        form = PageApp_MembersForm(initial={'location_buffer': '10'}) # An empty form
    
    rdict = {'object': page_app, 'members': organizations, 'media_path': settings.MEDIA_URL, 'base_url': base_url, 'direct_link': direct_link, 'search_form': search_form, 'form' : form, 'center': center_map}
    
    return render_view('page_members/index.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))


def detail_view(request, page_app, pk):
    member = get_object_or_404(Organization, pk=pk)
    return render_view('page_members/detail.html',
                       { 'member':  member, 'media_path': settings.MEDIA_URL },
                       MEDIAS,
                       context_instance=RequestContext(request))
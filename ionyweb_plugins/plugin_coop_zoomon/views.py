# -*- coding: utf-8 -*-
from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view
from coop_local.models import Organization, Exchange, Occurrence, Calendar
from ionyweb_plugins.page_coop_blog.models import CoopEntry
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.conf import settings

# from ionyweb.website.rendering.medias import CSSMedia, JSMedia, JSAdminMedia
MEDIAS = (
    # App CSS
    # CSSMedia('plugin_coop_zoomon.css'),
    # App JS
    # JSMedia('plugin_coop_zoomon.js'),
    # Actions JSAdmin
    # JSAdminMedia('plugin_coop_zoomon_actions.js'),
    )

def index_view(request, plugin):
    items = []
    agenda = get_object_or_404(Calendar, sites__id=settings.SITE_ID)
    
    organizations = None
    occ = None
    entries = None
    
    if plugin.filter == "events":
        occ = Occurrence.objects.filter(
                        event__zoom_on=True,
                        event__active=True,
                        event__calendar=agenda,
                        ).order_by("start_time")[:plugin.max_item]

    if plugin.filter == "entries":
        entries = CoopEntry.objects.filter(status=1, zoom_on=True).order_by('-modification_date')[:plugin.max_item]
        
    if plugin.filter == "organizations":        
        organizations = Organization.objects.filter(active=True, is_project=False, zoom_on=True).order_by("-modified")[:plugin.max_item]
    
    if occ:
        for o in occ :
            items.append({'type':'occ', 'obj': o})

    if organizations:
        for o in organizations :
            items.append({'type':'organization', 'obj': o})

    if entries:
        for e in entries :
            items.append({'type':'entry', 'obj': e})
 
    return render_view('plugin_coop_zoomon/index.html',
                       {'object': plugin, 'items': items, 'agenda_url': settings.COOP_AGENDA_URL, 'organization_url': settings.COOP_MEMBER_ORGANIZATIONS_URL},
                       MEDIAS,
                       context_instance=RequestContext(request))

# -*- coding: utf-8 -*-
from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from coop_local.models import Event, EventCategory, Occurrence
from django.conf import settings

from django.shortcuts import get_object_or_404

from ionyweb.website.rendering.medias import CSSMedia
from datetime import datetime

MEDIAS = (
    CSSMedia('plugin_coop_agenda.css'),
    )

def index_view(request, plugin):
    
    nb_events = plugin.nb_events
    if plugin.category != "":
        occ = Occurrence.objects.filter(
                            end_time__gt=datetime.now(),
                            event__active=True,
                            event__category__label=plugin.category
                            ).order_by("start_time")[:nb_events]
    else:
        occ = Occurrence.objects.filter(
                            end_time__gt=datetime.now(),
                            event__active=True
                            ).order_by("start_time")[:nb_events]
        
    agenda_url = plugin.agenda_url
    
    
    rdict = {'object': plugin, 'occ': occ, 'media_path': settings.MEDIA_URL, 'agenda_url': agenda_url}
    
    return render_view('plugin_coop_agenda/index.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))


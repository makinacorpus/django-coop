# -*- coding: utf-8 -*-
from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from coop_local.models import Organization

from django.conf import settings

from django.shortcuts import get_object_or_404

from ionyweb.website.rendering.medias import CSSMedia
from datetime import datetime

MEDIAS = (
    CSSMedia('plugin_coop_members.css'),
    )

def index_view(request, plugin):

    nb_members = plugin.nb_members
    members = Organization.objects.all().order_by("modified")[:nb_members]
        
    members_url = plugin.members_url
    
    
    rdict = {'object': plugin, 'members': members, 'media_path': settings.MEDIA_URL, 'members_url': members_url}
    
    return render_view('plugin_coop_members/index.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))


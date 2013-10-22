# -*- coding: utf-8 -*-
from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from coop_local.models import Organization
from django.conf import settings

from ionyweb.website.rendering.medias import CSSMedia
MEDIAS = (
    CSSMedia('plugin_coop_members_icons.css'),
    )
    
    
def index_view(request, plugin):
    
    if plugin.type != "":
        organizations = Organization.objects.filter(category__label=plugin.type).order_by('title')
    else:
        organizations = Organization.objects.all().order_by('title')
    
    return render_view('plugin_coop_members_icons/index.html',
                       {'object': plugin, 'members': organizations, 'media_path': settings.MEDIA_URL},
                       MEDIAS,
                       context_instance=RequestContext(request))                       
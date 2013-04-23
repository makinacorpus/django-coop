# -*- coding: utf-8 -*-
from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from coop_local.models import Exchange

from django.conf import settings

from django.shortcuts import get_object_or_404

from ionyweb.website.rendering.medias import CSSMedia
from datetime import datetime

MEDIAS = (
    CSSMedia('plugin_coop_exchange.css'),
    )

def index_view(request, plugin):

    nb_exchanges = plugin.nb_exchanges
    exchanges = Exchange.objects.all().order_by("modified")[:nb_exchanges]
        
    exchange_url = plugin.exchange_url
    
    
    rdict = {'object': plugin, 'exchanges': exchanges, 'media_path': settings.MEDIA_URL, 'exchange_url': exchange_url}
    
    return render_view('plugin_coop_exchange/index.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))


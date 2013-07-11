# -*- coding: utf-8 -*-
from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from ionyweb_plugins.page_coop_blog.models import CoopEntry
from django.conf import settings

from django.shortcuts import get_object_or_404

from ionyweb.website.rendering.medias import CSSMedia
from datetime import datetime

MEDIAS = (
    CSSMedia('plugin_coop_blog.css'),
    )

def index_view(request, plugin):
    
    nb_news = plugin.nb_news
    entries = CoopEntry.objects.filter(status=True
                            ).order_by("-publication_date")[:nb_news]

    blog_url = plugin.blog_url
    
    rdict = {'object': plugin, 'entries': entries, 'media_path': settings.MEDIA_URL, 'blog_url': blog_url}
    
    return render_view('plugin_coop_blog/index.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))


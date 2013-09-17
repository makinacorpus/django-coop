# -*- coding: utf-8 -*-
from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from django.conf import settings

from django.shortcuts import get_object_or_404

from django.template.loader import get_template
from django.template import Context
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import ugettext, ugettext_lazy as _

from ionyweb.website.rendering.medias import CSSMedia
from datetime import datetime
from forms import Plugin_CoopSearchGlobalForm

MEDIAS = (
    CSSMedia('plugin_coop_searchglobal.css'),
    )

def index_view(request, plugin):

    form = Plugin_CoopSearchGlobalForm()
    render_template = 'plugin_coop_searchglobal/index.html'
    rdict = {}
    rdict = {'object': plugin, 'search_results_url': settings.COOP_SEARCHRESULTS_URL, 'form': form}
    
    return render_view(render_template,
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))


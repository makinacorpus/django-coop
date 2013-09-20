# -*- coding: utf-8 -*-
from datetime import datetime

from django.template import RequestContext
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.template import Context
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import ugettext, ugettext_lazy as _

from ionyweb.website.rendering.utils import render_view
from ionyweb.website.rendering.medias import CSSMedia

from forms import Plugin_CoopTagCloudForm
from coop.base_models import Tag
from coop_local.models import Location, Area, Document, Exchange, Offer, Occurrence, Calendar, Organization

MEDIAS = (
    CSSMedia('plugin_coop_tagcloud.css'),
    )

def index_view(request, plugin):

    computed_tags = []

    # Get alls tags...
    all_tags = Tag.objects.all()
    
    # ...and see how they are used in objects, and make a tag cloud
    for tag in all_tags:
        try:
            items = tag.tagged_items()
            for item in items:
                nb = len(items.get(item))
                computed_tags.append({'name': tag, 'interest': nb})
            
        except:
            pass
    
    form = Plugin_CoopTagCloudForm()
    render_template = 'plugin_coop_tagcloud/index.html'
    rdict = {}
    rdict = {'object': plugin, 'search_results_url': settings.COOP_SEARCHRESULTS_URL, 'form': form, 'computed_tags': computed_tags}
    
    return render_view(render_template,
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))


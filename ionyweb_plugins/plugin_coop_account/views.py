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

from forms import Plugin_CoopAccountForm
from coop.base_models import Tag
from coop_local.models import Location, Area, Document, Exchange, Offer, Occurrence, Calendar, Organization

MEDIAS = (
    CSSMedia('plugin_coop_account.css'),
    )

def index_view(request, plugin):

    is_authent = request.user.is_authenticated()
    
    form = Plugin_CoopAccountForm()
    render_template = 'plugin_coop_account/index.html'
    rdict = {}
    rdict = {'object': plugin, 'form': form, 'is_authent': is_authent, 'url_account': plugin.account_url}
    
    return render_view(render_template,
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))


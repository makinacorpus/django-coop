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
from forms import Plugin_CoopPromoteForm

MEDIAS = (
    CSSMedia('plugin_coop_promote.css'),
    )

def index_view(request, plugin):

    form = Plugin_CoopPromoteForm()
    render_template = 'plugin_coop_promote/index.html'
    rdict = {}
    if request.user.is_authenticated():
        #form = GuestForm()
        #message = None
        #base_url = u'%s' % (plugin.get_absolute_url())

        if request.method == "GET" and not request.is_admin_url:
            form = Plugin_CoopPromoteForm(request.GET)
            if form.is_valid():

                dest = form.cleaned_data['dest'].strip()
                msg = form.cleaned_data['msg']

                plaintext = get_template('plugin_coop_promote/promote.txt')
                htmly     = get_template('plugin_coop_promote/promote.html')

                d = Context({ 'first_name': request.user.first_name , 'last_name': request.user.last_name, 'msg': msg })

                text_content = plaintext.render(d)
                html_content = htmly.render(d)

                title = _("Invitation to PES Auvergne")
                sender = "contact@echanges-solidaires-auvergne.fr"
                msg = EmailMultiAlternatives(title, text_content, sender, [dest])
                msg.attach_alternative(html_content, "text/html")
                
                try:
                    res = msg.send()
                    render_template = 'plugin_coop_promote/sent.html'
                except:   
                    render_template = 'plugin_coop_promote/not_sent.html'
                        
        rdict = {'object': plugin, 'media_path': settings.MEDIA_URL, 'form': form}
    
    return render_view(render_template,
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))


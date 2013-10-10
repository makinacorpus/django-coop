# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from ionyweb.website.rendering.medias import CSSMedia
from ionyweb.website.rendering.utils import render_view
from forms import Plugin_CoopContactForm

RENDER_MEDIAS = (
    CSSMedia('plugin_coop_contact.css'),
    )


def index_view(request, plugin):
	
    contact_form = Plugin_CoopContactForm(request.user)
    message = None

    if request.method == "POST" and not request.is_admin_url:
        # Check if we submit this form.
        if int(request.POST['contactform']) == plugin.pk:
            contact_form = Plugin_CoopContactForm(request.POST)
            if contact_form.is_valid():
                contact_form.send(plugin.emails, default_subject=plugin.subject)
                message = _(u'Message sent')
                contact_form = Plugin_CoopContactForm()
            else:
                message = _(u'The mail could not be sent')

    return render_view(
        plugin.get_templates('plugin_coop_contact/index.html'),
        {'object': plugin,
         'form': contact_form,
         'message': message},
        RENDER_MEDIAS)

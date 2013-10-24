# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext
from ionyweb.website.rendering.medias import CSSMedia
from ionyweb.website.rendering.utils import render_view
from forms import Plugin_CoopNewsletterForm, GuestNewsletterForm

MEDIAS = (
    CSSMedia('plugin_coop_newsletter.css'),
    )


def index_view(request, plugin):
    form = GuestNewsletterForm()
    message = None

    if request.method == "POST" and not request.is_admin_url:
        # Check if we submit this specific form.
        if int(request.POST['inscription_form']) == plugin.pk:
            form = GuestNewsletterForm(request.POST)
            if form.is_valid():
                form.save()
                message = _(u'Inscription saved')
                form = GuestNewsletterForm()
            else:
                message = _(u'There is some errors in your form.')

    return render_view('plugin_coop_newsletter/index.html',
                       {'object': plugin,
                        'form': form,
                        'message': message},
                       MEDIAS,
                       context_instance=RequestContext(request))

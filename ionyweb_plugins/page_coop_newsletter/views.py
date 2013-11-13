# -*- coding: utf-8 -*-

from django.utils.http import urlquote
from django.template.loader import get_template
from django.template import Context
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template import RequestContext
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.gis import geos
from django.contrib import messages
from django.contrib.gis.measure import D
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from tempfile import NamedTemporaryFile
import tempfile
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.http import http_date

import csv
from datetime import datetime, timedelta

from ionyweb.website.rendering.utils import render_view
from ionyweb.website.rendering.medias import CSSMedia

from .forms import PageApp_CoopNewsletterForm, GuestNewsletterForm
from .models import GuestNewsletter

MEDIAS = (
    CSSMedia('page_coop_newsletter.css'),
    )

def index_view(request, page_app):
    base_url = u'%s' % (page_app.get_absolute_url())
    form = GuestNewsletterForm()
    message = None

    if request.method == "POST" and not request.is_admin_url:
        # Check if we submit this specific form.
        if int(request.POST['inscription_form']) == page_app.pk:
            form = GuestNewsletterForm(request.POST)
            if form.is_valid():
                form.save()
                message = _(u'Inscription saved')
                form = GuestNewsletterForm()
            else:
                message = _(u'There is some errors in your form.')

    rdict = {'form': form, 'message': message, 'object': page_app}
    return render_view('page_coop_newsletter/index.html',
                        rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))

def export(request, page_app):
    # Export subscribers in CSV
    if request.user.is_authenticated() and request.user.is_superuser:
        list_subscribers = []
        guests = GuestNewsletter.objects.all()
        for g in guests:
            line = "%s,%s,%s" % (g.first_name, g.last_name, g.email)
            list_subscribers.append(line)

        # Create the .csv file
        output = None
        export = ""
        try:
            with tempfile.TemporaryFile('w', suffix='.wkt') as f:
                output = f.name

                export = "%s,%s,%s\n" % ('first_name', 'last_name', 'email')
                for line  in list_subscribers:
                    export = "%s%s\n" % (export, line)

                wrapper = FileWrapper(f)
                response = HttpResponse(export, content_type='application/txt')
                response['Last-Modified'] = http_date()
                response['Content-Length'] = len(export)
                response['Content-Disposition'] = 'attachment; filename=export_suscribers.csv'
        finally:
            pass

    messages.info(request,_(u"No data to export"))
    admin_url = "/admin/"
    return HttpResponseRedirect(admin_url)
        
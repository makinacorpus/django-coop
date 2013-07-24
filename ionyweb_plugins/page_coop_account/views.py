# -*- coding: utf-8 -*-

from django.utils.http import urlquote
import csv
from django.template.loader import get_template
from django.template import Context
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from coop_local.models import Organization, Event, EventCategory, Calendar, Occurrence, Exchange
from django.conf import settings

from django.shortcuts import get_object_or_404

from ionyweb.website.rendering.medias import CSSMedia
from datetime import datetime

from .forms import PageApp_CoopAccountForm

from django.db.models import Q

from django.contrib.gis import geos
from django.contrib.gis.measure import D
from coop_local.models import Location

from django.contrib.auth import authenticate, login, logout

from coop.org.models import get_rights as get_rights_org
from ionyweb_plugins.page_coop_blog.models import CoopEntry

MEDIAS = (
    CSSMedia('page_coop_account.css'),
    )

def index_view(request, page_app):
    base_url = u'%s' % (page_app.get_absolute_url())
    
    if request.method == 'POST': # If the login form has been submitted
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)        
    
    tab_org = []
    tab_projects = []
    tab_exchanges = []
    tab_events = []
    tab_entries = []

    if request.user.is_authenticated():
        render_page = 'page_coop_account/index.html'
        
        # My organizations
        organizations = Organization.objects.filter(is_project=False).order_by('title')
        for o in organizations:
            if request.user.is_superuser:
                can_edit = True
                can_add = True
            else:
                can_edit, can_add = get_rights_org(request, o.pk)
            if can_edit:
                tab_org.append(o)

        # My projects
        projects = Organization.objects.filter(is_project=True).order_by('title')
        for o in projects:
            if request.user.is_superuser:
                can_edit = True
                can_add = True
            else:
                can_edit, can_add = get_rights_org(request, o.pk)
            if can_edit:
                tab_projects.append(o)

        # My news
        if request.user.is_superuser:
            entries = CoopEntry.objects.all().order_by('title')
        else:
            entries = CoopEntry.objects.filter(author=request.user).order_by('title')
        for e in entries:
            tab_entries.append(e)
        
        # My exchanges
        exchanges = Exchange.objects.all().order_by('title')
        for e in exchanges:
            if request.user.is_superuser:
                can_edit = True
                can_add = True
            else:
                if e.organization:
                    can_edit, can_add = get_rights_org(request, e.organization.pk)
            if can_edit:
                tab_exchanges.append(e)
        
        # My events
        occs = Occurrence.objects.all().order_by('start_time')
        for o in occs:
            if request.user.is_superuser:
                can_edit = True
                can_add = True
            else:
                if o.event.organization:
                    can_edit, can_add = get_rights_org(request, o.event.organization.pk)
            if can_edit:
                tab_events.append(o)

    else:
        render_page = 'page_coop_account/login.html'
    
        
    rdict = {'object': page_app, 'base_url': base_url, 'org': tab_org, 'projects': tab_projects, 'exchanges': tab_exchanges, 'occs': tab_events, 'entries': tab_entries}
    
    return render_view(render_page,
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))

def logout_view(request, page_app):
    logout(request)
    base_url = u'%s' % (page_app.get_absolute_url())
    render_page = 'page_coop_account/login.html'
    rdict = {'object': page_app, 'base_url': base_url}
    
    return render_view(render_page,
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))


def detail_view(request, page_app, pk):
    event = get_object_or_404(Event, pk=pk)
    base_url = u'%sp/' % (page_app.get_absolute_url())
    rdict = {'object': page_app, 'e': event, 'media_path': settings.MEDIA_URL, 'base_url': base_url}
    return render_view('page_coop_account/detail.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))                


def mailing_view(request, page_app):    
    if request.user.is_superuser:
        dest_file = csv.DictReader(open("/tmp/emails_test.csv", 'rb'), delimiter=';', quotechar='"')        
        for line, _row in enumerate(dest_file):
            row = {}
            for k, v in _row.iteritems():
                row[k.decode('utf8')] = v.decode('utf8')

            title = "ERRATUM - Rejoindre la plate-forme d'échanges solidaires en Auvergne"
            sender = "contact@echanges-solidaires-auvergne.fr"
            dest = row[u'email'].strip()
            
            login = row[u'username'].strip()
            password = row[u'password'].strip()
            
            if login.endswith(".") and len(login) > 1:
                before = login
                login = before[:-1]
            
            plaintext = get_template('page_coop_account/mailing_pes.txt')
            htmly     = get_template('page_coop_account/mailing_pes.html')

            d = Context({ 'login': login , 'password': password})

            text_content = plaintext.render(d)
            html_content = htmly.render(d)

            msg = EmailMultiAlternatives(title, text_content, sender, [dest])
            msg.attach_alternative(html_content, "text/html")
            
            handle1 = open('/tmp/res_emailing.txt','a+')
            try:
                res = msg.send()                
                handle1.write("Sent : %s\n" % (dest))
                
            except:   
                handle1.write("NOT Sent : %s\n" % (dest))
                print "No email sent"
            handle1.close();
    
        rdict = {'object': page_app}
        return render_view('page_coop_account/mailing_end.html',
                    rdict,
                    MEDIAS,
                    context_instance=RequestContext(request))                

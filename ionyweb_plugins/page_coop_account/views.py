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
from django.contrib.gis.measure import D
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.http import HttpResponseRedirect

from registration.forms import RegistrationForm

from math import pi
import csv
from datetime import datetime, timedelta

from ionyweb.website.rendering.utils import render_view
from ionyweb.website.rendering.medias import CSSMedia
from ionyweb_plugins.page_coop_blog.models import CoopEntry
from coop_local.models import Organization, Event, EventCategory, Calendar, Occurrence, Exchange, Person, Location, PersonPreferences
from coop.org.models import get_rights as get_rights_org
from .forms import PageApp_CoopAccountForm, PageApp_CoopAccountPreferencesForm, PageApp_CoopRegistrationForm
from .models import AccountRegistrationView

MEDIAS = (
    CSSMedia('page_coop_account.css'),
    )

def index_view(request, page_app):
    base_url = u'%s' % (page_app.get_absolute_url())
    edit_url = None
    
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
    tab_private_entries = []
    logo = None
    person = None
    user_pref_matches = None

    if request.user.is_authenticated():
        render_page = 'page_coop_account/index.html'
        
        person = Person.objects.filter(user=request.user)
        if person:
            person = person[0]
         
            if person.prefs:
                user_pref = PersonPreferences.objects.get(id=person.prefs.pk)
            else:
                # If preferences do not exist, create them
                user_pref = PersonPreferences()
                user_pref.save()
                person.prefs = user_pref
                person.save()

            org = Organization.objects.filter(members=person)
            if org:
                logo = org[0].logo

                
        if person:
            edit_url = u'%sp/pref_edit/%s' % (page_app.get_absolute_url(),user_pref.pk)

            user_pref_matches = get_user_pref_matches(user_pref, settings.NOTIFICATION_MY_ACCOUNT_DELTA)
                
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
        
        # Private news
        my_groups = request.user.groups.all()
        for g in my_groups:
            tab_private_entries = CoopEntry.objects.filter(group_private=g).order_by('title')
        
        # My exchanges
        exchanges = Exchange.objects.filter(person=person).order_by('title')
        for e in exchanges:
            tab_exchanges.append(e)

        # My events
        occs = Occurrence.objects.filter(event__person=person).order_by('start_time')
        for o in occs:
            tab_events.append(o)

    else:
        render_page = 'page_coop_account/login.html'
    
    exchanges_url = settings.COOP_EXCHANGE_EXCHANGES_URL
    organizations_url = settings.COOP_MEMBER_ORGANIZATIONS_URL
    agenda_url = settings.COOP_AGENDA_URL
    blog_url = settings.COOP_BLOG_URL

    rdict = {'object': page_app, 'base_url': base_url, 'edit_url': edit_url, 'org': tab_org, 'projects': tab_projects, 'exchanges': tab_exchanges, 'occs': tab_events, 'entries': tab_entries, 'private_entries': tab_private_entries, 'logo': logo, 'media_path': settings.MEDIA_URL, 'person': person, 'items': user_pref_matches, 'exchanges_url': exchanges_url, 'organizations_url': organizations_url, 'agenda_url': agenda_url, 'blog_url': blog_url}
    
    return render_view(render_page,
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))

def get_user_pref_matches(pref, delta):
    
    items = []
    exchanges = None
    events = None
    organizations = None
    entries = None

    delta_days = datetime.now() - timedelta(days=delta)

    for tc in pref.type_content.all():
        if tc.name == "exchanges":
            exchanges = Exchange.objects.filter(active=True).order_by("-modified")
            arg = Q(created__gt=delta_days)
            arg = arg | Q(modified__gt=delta_days)
            for activity in pref.activities.all():
                arg = arg | Q(activity__label__icontains=activity)
                
            for theme in pref.transverse_themes.all():
                arg = arg | Q(transverse_themes__name__icontains=theme)
                
            for area in pref.locations.all():
                possible_locations = get_possible_locations(area, pref.locations_buffer)
                arg = arg| Q(location__in=possible_locations)
            
            for org in pref.organizations.all():
                arg = arg | Q(organization=org)
                
            exchanges = exchanges.filter(arg).distinct()

        if tc.name == "events":
            agenda = get_object_or_404(Calendar, sites__id=settings.SITE_ID)
            occs = Occurrence.objects.filter(
                                end_time__gt=datetime.now(),
                                event__active=True,
                                event__calendar=agenda,
                                ).order_by("start_time")
            
            arg = Q(event__created__gt=delta_days) 
            arg = arg | Q(event__modified__gt=delta_days)

            for activity in pref.activities.all():
                arg = arg | Q(event__activity__label__icontains=activity)
                
            for theme in pref.transverse_themes.all():
                arg = arg | Q(event__transverse_themes__name__icontains=theme)
                
            for area in pref.locations.all():
                possible_locations = get_possible_locations(area, pref.locations_buffer)
                arg = arg| Q(event__location__in=possible_locations)
            
            for org in pref.organizations.all():
                arg = arg | Q(event__organization=org)
            
            occs = occs.filter(arg).distinct()
            
        if tc.name == "organizations":
            organizations = Organization.objects.filter(active=True, is_project=False).order_by("-modified")
            
            arg = Q(created__gt=delta_days)
            arg = arg | Q(modified__gt=delta_days)
            
            for activity in pref.activities.all():
                arg = arg | Q(offer__activity__label__icontains=activity)
                
            for theme in pref.transverse_themes.all():
                arg = arg | Q(transverse_themes__name__icontains=theme)
                
            for area in pref.locations.all():
                possible_locations = get_possible_locations(area, pref.locations_buffer)
                arg = arg| Q(located__location__in=possible_locations)
            
            for org in pref.organizations.all():
                arg = arg | Q(pk=org.pk)
            
            organizations = organizations.filter(arg).distinct()
            
        if tc.name == "entries":
            entries = CoopEntry.objects.filter(status=1, group_private__isnull=True).order_by('-modification_date')
            
            arg = Q(creation_date__gt=delta_days)
            arg = arg | Q(modification_date__gt=delta_days)
            
            for activity in pref.activities.all():
                arg = arg | Q(activity__label__icontains=activity)
                
            for theme in pref.transverse_themes.all():
                arg = arg | Q(transverse_themes__name__icontains=theme)
                
            for org in pref.organizations.all():
                arg = arg | Q(pk=org.pk)
            
            entries = entries.filter(arg).distinct()

    if exchanges:
        for e in exchanges :
            items.append({'type':'exchange', 'obj': e})
    if events:
        for o in occs :
            items.append({'type':'occ', 'obj': o})
    if organizations:
        for o in organizations :
            items.append({'type':'organization', 'obj': o})
    if entries:
        for e in entries :
            items.append({'type':'entry', 'obj': e})
    
    return items


def get_possible_locations(area, radius):
    if not radius:
        radius = 0
    distance_degrees = (360 * radius) / (pi * 6378)
    zone = area.polygon.buffer(distance_degrees)
    zone_json = zone.json
    possible_locations = Location.objects.filter(point__intersects=zone)
    return possible_locations


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
    person = get_object_or_404(Person, pk=pk)
    base_url = u'%sp/' % (page_app.get_absolute_url())
    rdict = {'object': page_app, 'p': person, 'media_path': settings.MEDIA_URL, 'base_url': base_url}
    return render_view('page_coop_account/detail.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))                


def editpref_view(request, page_app, user_id=None):
    
    if request.user.is_authenticated():
        person = Person.objects.filter(user=request.user)[0]
        if person.prefs:
            user_pref = PersonPreferences.objects.get(id=person.prefs.pk)
        else:
            # If preferences do not exist, create them
            user_pref = PersonPreferences()
            user_pref.save()
            person.prefs = user_pref
            person.save()

        base_url = u'%s' % (page_app.get_absolute_url())
        edit_url = u'%sp/pref_edit/%s' % (page_app.get_absolute_url(),user_pref.pk)

        if request.method == 'POST': # If the form has been submitted
        
            form = PageApp_CoopAccountPreferencesForm(request.POST, instance = user_pref)
            
            if form.is_valid():
                user_pref = form.save()
                
                rdict = {'base_url': base_url}
                return redirect(base_url)
        else:
            form = PageApp_CoopAccountPreferencesForm(instance = user_pref)
        
        rdict = {'media_path': settings.MEDIA_URL, 'base_url': base_url, 'edit_url': edit_url, 'form': form}
        return render_view('page_coop_account/edit.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request))
    else:
        return render_view('page_coop_account/forbidden.html')

                       
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


def register_view(request, page_app):
    
    base_url = u'%s' % (page_app.get_absolute_url())

    if request.method == 'POST': # If the form has been submitted
    
        form = PageApp_CoopRegistrationForm(request.POST)
        
        if form.is_valid():
            user = AccountRegistrationView.register_user(request, **form.cleaned_data)
            
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            
            # create a Person associated to this account
            person = Person()
            person.username = username
            person.first_name = firstname
            person.last_name = lastname
            person.user_id = user.id
            person.email = email
            person.save()
            
            return render_view('page_coop_account/registration_complete.html')
    else:
        form = PageApp_CoopRegistrationForm()
    
    rdict = {'media_path': settings.MEDIA_URL, 'base_url': base_url, 'form': form}
    return render_view('page_coop_account/registration_form.html',
                    rdict,
                    MEDIAS,
                    context_instance=RequestContext(request))


# -*- coding: utf-8 -*-

from django.template import RequestContext
from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.gis import geos
from django.core.mail import send_mail
from django.utils.simplejson import dumps
from django.db.models import Q
from django.utils.simplejson import dumps
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.contrib.sites.models import Site

from datetime import datetime
from math import pi
import json

from coop.exchange.admin import ExchangeForm
from coop_local.models import Exchange, Location, Area, Document, Person, Organization
from coop.org.models import get_rights
from coop.base_models import Tag
from .forms import PageApp_CoopExchangeSearchForm, PartialExchangeForm, DocumentForm, ReplyExchangeForm
from coop_local.utils import notify_object_creation, user_linked_to_organization

from ionyweb.website.rendering.utils import render_view
from ionyweb.website.rendering.medias import CSSMedia

MEDIAS = (
    CSSMedia('page_coop_exchange.css'),
)

def index_view(request, page_app):
    rdict = filter_data(request, page_app, "list")
    return render_view('page_coop_exchange/index.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))                           


def carto_view(request, page_app):
    rdict = filter_data(request, page_app, "carto")    
    return render_view('page_coop_exchange/index_carto.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request)) 


def filter_data(request, page_app, mode):
    base_url = u'%s' % (page_app.get_absolute_url())

    exchanges = Exchange.objects.filter(active=True, status='V').order_by("-modified")
    exchanges = exchanges.filter(Q(start__lte=datetime.today()) | Q(start__isnull=True) )   

    more_criteria = False
    is_exchange = True
    
    search_form_template = "page_coop_exchange/search_form_exchange.html"
    
    if request.method == 'GET': # If the form has been submitted        
        form = PageApp_CoopExchangeSearchForm(request.GET)
        if form.is_valid():
            if form.cleaned_data['free_search']:
                exchanges = exchanges.filter(Q(title__contains=form.cleaned_data['free_search']) | Q(description__contains=form.cleaned_data['free_search']) | Q(tagged_items__tag__name__in=[form.cleaned_data['free_search']]))
            
            if form.cleaned_data['type_exchange']:
                exchanges = exchanges.filter(Q(eway__in=form.cleaned_data['type_exchange']))

            if form.cleaned_data['type']:
                exchanges = exchanges.filter(Q(etype__in=form.cleaned_data['type']))

            if form.cleaned_data['thematic'] or form.cleaned_data['thematic2']:
                arg = Q()
                if form.cleaned_data['thematic']: 
                    arg = Q(transverse_themes=form.cleaned_data['thematic'])
                if form.cleaned_data['thematic2']: 
                    arg = arg | Q(transverse_themes=form.cleaned_data['thematic2'])
                exchanges = exchanges.filter(arg)
            
            if form.cleaned_data['activity'] and form.cleaned_data['activity2']:
                activity = form.cleaned_data['activity']
                activity2 = form.cleaned_data['activity2']
                
                tab_keep = get_list_exch_to_keep(exchanges, activity)
                tab_keep2 = get_list_exch_to_keep(exchanges, activity2)
                exchanges = exchanges.filter(Q(pk__in=tab_keep) | Q(pk__in=tab_keep2) )

            else:
                if form.cleaned_data['activity']:
                    activity = form.cleaned_data['activity']                    
                    tab_keep = get_list_exch_to_keep(exchanges, activity)
                    exchanges = exchanges.filter(pk__in=tab_keep)
                else:
                    if form.cleaned_data['activity2']:
                        activity = form.cleaned_data['activity2']                    
                        tab_keep = get_list_exch_to_keep(exchanges, activity)
                        exchanges = exchanges.filter(pk__in=tab_keep)
                
                
            if form.cleaned_data['location']:
                label = form.cleaned_data['location']
                pk = form.cleaned_data['location_id']
                try:
                    area = Area.objects.get(pk=pk)
                except Area.DoesNotExist:
                    area = None
    
                if area :
                    radius = form.cleaned_data['location_buffer']
                    if not radius:
                        radius = 0                
                    distance_degrees = (360 * radius) / (pi * 6378)
                    zone = area.polygon.buffer(distance_degrees)
                    # Get the possible location in the buffer...
                    possible_locations = Location.objects.filter(point__intersects=zone)
                    # ...and filter organization according to these locations
                    exchanges = exchanges.filter(Q(location__in=possible_locations))
            
            if form.cleaned_data['method']:
                exchanges = exchanges.filter(Q(methods__in=form.cleaned_data['method']))
            
            if form.cleaned_data['skills']:
                exchanges = exchanges.filter(Q(methods__in=form.cleaned_data['skills']))

            if request.GET.get('more_criteria_status'):
                if request.GET['more_criteria_status'] == 'True':
                    more_criteria = True

                
    else:
        form = PageApp_CoopExchangeSearchForm({'location_buffer': '10'}) # An empty form
        more_criteria = False
    
    center_map = settings.COOP_MAP_DEFAULT_CENTER
    
    # Get available locations for autocomplete
    available_locations = dumps([{'label':area.label, 'value':area.pk} for area in Area.objects.all().order_by('label')])

    # Get exchange title and tags for free search autocomplete
    tab_available_data = [{'label':e.title, 'value':e.pk} for e in Exchange.objects.filter(Q(active=True)).order_by("-modified")]
    tab_available_data += [{'label':t.name, 'value':t.pk} for t in Tag.objects.all().order_by('name')]
    available_data = dumps(tab_available_data)
   
    if mode == 'list':
        paginator = Paginator(exchanges, 10)
        page = request.GET.get('page')
        try:
            exchanges_page = paginator.page(page)
        except PageNotAnInteger:
            exchanges_page = paginator.page(1)
        except EmptyPage:
            exchanges_page = paginator.page(paginator.num_pages)
        get_params = request.GET.copy()
        if 'page' in get_params:
            del get_params['page'] 
    else:
        exchanges_page = exchanges
        get_params = request.GET.copy()    
    
    
    rdict = {'exchanges': exchanges_page, 'base_url': base_url, 'form': form, 'center': center_map, 'more_criteria': more_criteria, 'available_locations': available_locations, 'available_data': available_data, 'search_form_template': search_form_template, 'mode': mode, 'media_path': settings.MEDIA_URL, 'is_exchange': is_exchange}
    
    return rdict


def get_list_exch_to_keep(exchanges, activity):    
    tab_keep = []
    for e in exchanges:
        if e.activity:
            parent = get_parent_activity_leve_0(e.activity)
            if parent == activity.label:
                tab_keep.append(e.pk)
    return tab_keep

def get_parent_activity_leve_0(activity):
    if activity.parent:
        return get_parent_activity_leve_0(activity.parent)
    else:
        return activity.label

        
def detail_view(request, page_app, pk):
    e = get_object_or_404(Exchange, pk=pk)
    base_url = u'%sp/' % (page_app.get_absolute_url())
    imgs = e.document_set.filter(type__name='Galerie')
    docs = e.document_set.exclude(type__name='Galerie')
    default_center = settings.COOP_MAP_DEFAULT_CENTER
    print_css = 0
    if request.method == 'GET' and 'mode' in request.GET:
        if request.GET['mode'] == 'print':
            print_css = 1    
    
    point = None
    if e.location.point:
        point = e.location.point
    else:
        # then take first address of the organization
        if e.organization:
            for l in e.organization.located.all():
                if l.location.point:
                    point = l.location.point
    
    rdict = {'object': page_app, 'e': e, 'media_path': settings.MEDIA_URL,'imgs': imgs, 'docs': docs, 'base_url': base_url, 'media_path': settings.MEDIA_URL, 'default_center': default_center, 'point': point, 'print_css': print_css}
    return render_view('page_coop_exchange/detail.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))


def add_view(request, page_app, exchange_id=None):

    if Site._meta.installed:
        site = Site.objects.get_current()
    else:
        site = RequestSite(request)
    
    if request.user.is_authenticated():
        #base_url = u'%sp/exchange_add' % (page_app.get_absolute_url())
        center_map = settings.COOP_MAP_DEFAULT_CENTER
        DocFormSet = generic_inlineformset_factory(Document, form=DocumentForm, extra=1)

        status = 'P'
        if user_linked_to_organization(request.user):
            status = 'V'
        status_display = False
        if request.user.is_superuser:
            status = 'V'
            status_display = True
        
        if exchange_id:
            # update
            mode = 'update'
            exchange = get_object_or_404(Exchange, pk=exchange_id)
            base_url = u'%sp/exchange_edit/%s' % (page_app.get_absolute_url(),exchange_id)
            delete_url = u'%sp/exchange_delete/%s' % (page_app.get_absolute_url(),exchange_id)
            status = exchange.status
        else :
            # new
            mode = 'add'
            base_url = u'%sp/exchange_add' % (page_app.get_absolute_url())
            delete_url = ''
            exchange = Exchange()
        
        
        if request.method == 'POST': # If the form has been submitted        
            #exchange = Exchange()
            person = Person.objects.filter(user=request.user)
            if person:
                person = person[0]
                if mode == 'add':
                    # automatic association of the user to this exchange
                    exchange.person = person
            
            form = PartialExchangeForm(request.user, request.POST, request.FILES, instance = exchange)
            docFormset = DocFormSet(request.POST, request.FILES, prefix='doc', instance=exchange)
            
            if form.is_valid() and docFormset.is_valid():
                exchange = form.save()
                form.save_m2m()
                docFormset.save()
                
                if not request.user.is_superuser :
                    exchange.status = status
                    
                exchange.save()
                
                # notify the admin
                if mode == "add" and not user_linked_to_organization(request.user):
                    url = 'http://%s%sp/%s' % (site, settings.COOP_EXCHANGE_EXCHANGES_URL, exchange.pk)
                    notify_object_creation(url)
                
                base_url = u'%s' % (page_app.get_absolute_url())
                rdict = {'base_url': base_url, 'exchange_id': exchange.id}
                return render_view('page_coop_exchange/add_success.html',
                                rdict,
                                MEDIAS,
                                context_instance=RequestContext(request))
        else:
            form = PartialExchangeForm(request.user, instance=exchange) # An empty form
            docFormset = DocFormSet(instance=exchange, prefix='doc')
        
        app_root_url = u'%s' % (page_app.get_absolute_url())
        rdict = {'media_path': settings.MEDIA_URL, 'base_url': base_url, 'app_root_url': app_root_url, 'delete_url': delete_url, 'form': form, 'doc_form': docFormset, 'center': center_map, 'mode': mode,  'status_display': status_display}
        return render_view('page_coop_exchange/add.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request))
    else:
        return render_view('page_coop_exchange/forbidden.html')


def reply_view(request, page_app, exchange_id=None):
    if request.user.is_authenticated():
        base_url = u'%sp/exchange_reply/%s' % (page_app.get_absolute_url(),exchange_id)
        if request.method == 'POST': # If the form has been submitted        
            form = ReplyExchangeForm(request.user,request.POST)
            
            if form.is_valid():
                title = form.cleaned_data['title']
                response = form.cleaned_data['response']
                email = form.cleaned_data['email']
                tel = form.cleaned_data['tel']
                name = form.cleaned_data['name']
                
                # Add name, tel, mail to the content
                response = "%s\n\n%s\n%s\n%s" % (response, name, email, tel)
                try:
                    exchange = Exchange.objects.get(pk=exchange_id)
                except Area.DoesNotExist:
                    exchange = None
                
                send_ok = False
                if exchange and exchange.organization:
                    if exchange.organization.pref_email:
                        try :
                            # send email
                            send_mail(title, response, email, [exchange.organization.pref_email.content ], fail_silently=False)
                            send_ok = True
                        except:
                            pass
                    else:
                        if exchange.contact:
                            try :
                                # send email
                                send_mail(title, response, email, [contact ], fail_silently=False)
                                send_ok = True
                            except:
                                pass
                
                template = "page_coop_exchange/reply_success.html"
                if not send_ok:
                    template = "page_coop_exchange/reply_fail.html"

                base_url = u'%s' % (page_app.get_absolute_url())
                rdict = {'base_url': base_url, 'exchange_id': exchange.id}
                return render_view(template,
                            rdict,
                            MEDIAS,
                            context_instance=RequestContext(request))
                
        else:
            form = ReplyExchangeForm(user=request.user) # An empty form
        
        rdict = {'media_path': settings.MEDIA_URL, 'base_url': base_url, 'form': form}
        return render_view('page_coop_exchange/reply.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request))
    else:
        return render_view('page_coop_exchange/forbidden.html')


def delete_view(request, page_app, exchange_id):
    # check rights    
    if request.user.is_superuser:
        can_edit = True
    else:
        # Check if the current user is the owner
        person = Person.objects.filter(user=request.user)
        if person:
            person = person[0]
            exchange = Exchange.objects.get(pk=exchange_id)
            if exchange.person == person:
                can_edit = True
        
        if not can_edit:
            can_edit, can_add = get_rights(request, Exchange.objects.get(pk=exchange_id).organization.pk)

    if can_edit :
        u = Exchange.objects.get(pk=exchange_id).delete()
        base_url = u'%s' % (page_app.get_absolute_url())
        rdict = {'base_url': base_url}
        return render_view('page_coop_exchange/delete_success.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request))
    else:
        return render_view('page_coop_exchange/forbidden.html')


def get_org_infos(request, page_app, org_id):
    org = Organization.objects.filter(pk=org_id)
    if org:
        org = org[0]
        response_data = {}
        if org.pref_email:
            response_data['email'] = org.pref_email.content
        elif org.email:
            response_data['email'] = org.email
            
        if org.pref_phone:
            response_data['phone'] = org.pref_phone.content
        return HttpResponse(json.dumps(response_data), content_type="application/json")


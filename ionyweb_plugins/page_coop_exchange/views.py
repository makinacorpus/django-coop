# -*- coding: utf-8 -*-

from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from coop_local.models import Exchange
from coop_local.models import Location

from django.conf import settings

from django.shortcuts import get_object_or_404

from ionyweb.website.rendering.medias import CSSMedia
from datetime import datetime

from .forms import PageApp_CoopExchangeForm, PartialExchangeForm, DocumentForm, ReplyExchangeForm

from django.db.models import Q

from django.contrib.gis import geos
from coop_local.models import Location, Area, Document
from math import pi
from django.utils.simplejson import dumps

from django.contrib.contenttypes.generic import generic_inlineformset_factory
from coop.exchange.admin import ExchangeForm

from django.core.mail import send_mail

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

    exchanges = Exchange.objects.all()
    more_criteria = False
    
    if base_url == settings.COOP_EXCHANGE_SERVICES_URL:
        exchanges = exchanges.filter(organization__isnull=True)
        search_form_template = "page_coop_exchange/search_form_service.html"
    if base_url == settings.COOP_EXCHANGE_EXCHANGES_URL:
        exchanges = exchanges.filter(organization__isnull=False)
        search_form_template = "page_coop_exchange/search_form_exchange.html"
    
    if request.method == 'POST': # If the form has been submitted        
        form = PageApp_CoopExchangeForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['free_search']:
                exchanges = exchanges.filter(Q(title__contains=form.cleaned_data['free_search']) | Q(description__contains=form.cleaned_data['free_search']))
            
            if form.cleaned_data['type_exchange']:
                exchanges = exchanges.filter(Q(eway__in=form.cleaned_data['type_exchange']))

            if form.cleaned_data['type']:
                exchanges = exchanges.filter(Q(etype__in=form.cleaned_data['type']))

            if form.cleaned_data['thematic'] or form.cleaned_data['thematic2']:
                exchanges = exchanges.filter(Q(transverse_themes=form.cleaned_data['thematic']) | Q(transverse_themes=form.cleaned_data['thematic2']))
            
            if form.cleaned_data['activity'] or form.cleaned_data['activity2']:
                exchanges = exchanges.filter(Q(activity=form.cleaned_data['activity']) | Q(activity=form.cleaned_data['activity2']))
                
                
            if form.cleaned_data['location']:
                label = form.cleaned_data['location']
                pk = form.cleaned_data['location_id']
                area = get_object_or_404(Area, pk=pk)
                radius = form.cleaned_data['location_buffer']
                distance_degrees = (360 * radius) / (pi * 6378)
                zone = area.polygon.buffer(distance_degrees)
                 # Get the possible location in the buffer...
                possible_locations = Location.objects.filter(point__intersects=zone)
                # ...and filter organization according to these locations
                exchanges = exchanges.filter(Q(location__in=possible_locations))
            
            #TODO : mode
            
            #TODO : skills
            
            #TODO : warranty
            
            #TODO : organization
            
    else:
        form = PageApp_CoopExchangeForm({'location_buffer': '10'}) # An empty form
        more_criteria = False
    
    center_map = settings.COOP_MAP_DEFAULT_CENTER
    
    # Get available locations for autocomplete
    available_locations = dumps([{'label':area.label, 'value':area.pk} for area in Area.objects.all().order_by('label')])
    
    rdict = {'exchanges': exchanges, 'base_url': base_url, 'form': form, 'center': center_map, 'more_criteria': more_criteria, 'available_locations': available_locations, "search_form_template": search_form_template, "mode": mode, 'media_path': settings.MEDIA_URL}
    
    return rdict
                       
                       
def detail_view(request, page_app, pk):
    e = get_object_or_404(Exchange, pk=pk)
    base_url = u'%sp/' % (page_app.get_absolute_url())
    imgs = e.document_set.filter(type__name='Galerie')
    docs = e.document_set.exclude(type__name='Galerie')    
    rdict = {'object': page_app, 'e': e, 'media_path': settings.MEDIA_URL,'imgs': imgs, 'docs': docs, 'base_url': base_url, 'media_path': settings.MEDIA_URL}
    return render_view('page_coop_exchange/detail.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))


def add_view(request, page_app, exchange_id=None):
    if request.user.is_authenticated():
        #base_url = u'%sp/exchange_add' % (page_app.get_absolute_url())
        center_map = settings.COOP_MAP_DEFAULT_CENTER
        DocFormSet = generic_inlineformset_factory(Document, form=DocumentForm, extra=1)

        if exchange_id:
            # update
            mode = 'update'
            exchange = get_object_or_404(Exchange, pk=exchange_id)
            base_url = u'%sp/exchange_edit/%s' % (page_app.get_absolute_url(),exchange_id)

        else :
            # new
            mode = 'add'
            base_url = u'%sp/exchange_add' % (page_app.get_absolute_url())
            exchange = Exchange()
        
        
        if request.method == 'POST': # If the form has been submitted        
            #exchange = Exchange()
            form = PartialExchangeForm(request.POST, request.FILES, instance = exchange)
            docFormset = DocFormSet(request.POST, request.FILES, prefix='doc', instance=exchange)
            
            if form.is_valid() and docFormset.is_valid():
                exchange = form.save()
                docFormset.save()
                base_url = u'%s' % (page_app.get_absolute_url())
                rdict = {'base_url': base_url, 'exchange_id': exchange.id}
                return render_view('page_coop_exchange/add_success.html',
                                rdict,
                                MEDIAS,
                                context_instance=RequestContext(request))
        else:
            form = PartialExchangeForm(instance=exchange) # An empty form
            docFormset = DocFormSet(instance=exchange, prefix='doc')
        
        rdict = {'media_path': settings.MEDIA_URL, 'base_url': base_url, 'form': form, 'doc_form': docFormset, 'center': center_map, 'mode': mode}
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
            form = ReplyExchangeForm(request.POST)
            
            if form.is_valid():
                title = form.cleaned_data['title']
                response = form.cleaned_data['response']
                email = form.cleaned_data['email']
                
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
            form = ReplyExchangeForm() # An empty form
        
        rdict = {'media_path': settings.MEDIA_URL, 'base_url': base_url, 'form': form}
        return render_view('page_coop_exchange/reply.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request))
    else:
        return render_view('page_coop_exchange/forbidden.html')


                                              
# -*- coding: utf-8 -*-

from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from coop_local.models import Organization, Offer, Document, Reference, Relation, Engagement, Person, Contact, ActivityNomenclature, Location, Area

from django.conf import settings

from django.shortcuts import get_object_or_404

from ionyweb.website.rendering.medias import CSSMedia

from .forms import PageApp_MembersForm, PartialMemberForm, CustomLocatedForm, DocumentForm, CustomOfferForm, CustomRelationForm

from django.db.models import Q
from django.forms.models import inlineformset_factory, formset_factory
from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from django.contrib.gis import geos
from coop.base_models import Located
from coop.org.models import get_rights

from django.utils.simplejson import dumps

from math import pi


MEDIAS = (
    CSSMedia('page_members.css'),
    )

def index_view(request, page_app):    
    rdict = filter_data(request, page_app, "list")
    return render_view('page_members/index.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))                           


def carto_view(request, page_app):
    rdict = filter_data(request, page_app, "carto")    
    return render_view('page_members/index_carto.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request)) 

def filter_data(request, page_app, mode):
    # check rights    
    #can_edit, can_add = get_rights(request)

    is_project = is_obj_project(page_app)
    
    if page_app.type != "":
        organizations = Organization.objects.filter(category__label=page_app.type)
    else:
        organizations = Organization.objects.all()

    # show only published objects
    organizations = organizations.filter(active=True).order_by("title")
        
    base_url = u'%s' % (page_app.get_absolute_url())
    
    direct_link = False
    if page_app.type == settings.COOP_PARTENAIRE_LABEL:
        direct_link = True
    
    try:
        search_form = settings.COOP_MEMBER_SEARCH_FORM
    except:
        search_form = False

    center_map = settings.COOP_MAP_DEFAULT_CENTER

    if base_url == settings.COOP_MEMBER_ORGANIZATIONS_URL:
        organizations = organizations.filter(is_project=False)
        search_form_template = "page_members/search_form_organization.html"
    if base_url == settings.COOP_MEMBER_PROJECTS_URL:
        organizations = organizations.filter(is_project=True)
        search_form_template = "page_members/search_form_project.html"
    
    
    #if request.method == 'POST': # If the form has been submitted
        #form = PageApp_MembersForm(request.POST)
    if request.method == 'GET': # If the form has been submitted
        form = PageApp_MembersForm(request.GET)
        if form.is_valid():
            if form.cleaned_data['free_search']:
                organizations = organizations.filter(Q(title__icontains=form.cleaned_data['free_search']) | Q(description__icontains=form.cleaned_data['free_search']))

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
                    organizations = organizations.filter(Q(located__location__in=possible_locations))
                

            if form.cleaned_data['thematic'] or form.cleaned_data['thematic2']:
                organizations = organizations.filter(Q(transverse_themes=form.cleaned_data['thematic']) | Q(transverse_themes=form.cleaned_data['thematic2']))

            if form.cleaned_data['activity'] and form.cleaned_data['activity2']:
                activity = form.cleaned_data['activity']
                activity2 = form.cleaned_data['activity2']
                
                tab_keep = get_list_org_to_keep(organizations, activity)
                tab_keep2 = get_list_org_to_keep(organizations, activity2)
                organizations = organizations.filter(Q(pk__in=tab_keep) | Q(pk__in=tab_keep2) )
            else:
                if form.cleaned_data['activity']:
                    activity = form.cleaned_data['activity']                    
                    tab_keep = get_list_org_to_keep(organizations, activity)
                    organizations = organizations.filter(pk__in=tab_keep)
                else:
                    if form.cleaned_data['activity2']:
                        activity = form.cleaned_data['activity2']                    
                        tab_keep = get_list_org_to_keep(organizations, activity)
                        organizations = organizations.filter(pk__in=tab_keep)

            if form.cleaned_data['statut'] and form.cleaned_data['statut2']:
                organizations = organizations.filter(Q(legal_status=form.cleaned_data['statut']) | Q(legal_status=form.cleaned_data['statut2']))
            else:
                if form.cleaned_data['statut']:
                    organizations = organizations.filter(Q(legal_status=form.cleaned_data['statut']))
                else:
                    if form.cleaned_data['statut2']:
                        organizations = organizations.filter(Q(legal_status=form.cleaned_data['statut2']))
                
    else:
        form = PageApp_MembersForm(initial={'location_buffer': '10'}) # An empty form

    
    paginator = Paginator(organizations, 10)
    page = request.GET.get('page')
    try:
        orgs_page = paginator.page(page)
    except PageNotAnInteger:
        orgs_page = paginator.page(1)
    except EmptyPage:
        orgs_page = paginator.page(paginator.num_pages)
    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']    
    
    # Get available locations for autocomplete
    available_locations = dumps([{'label':area.label, 'value':area.pk} for area in Area.objects.all().order_by('label')])

    # Get organization title for free search autocomplete
    available_orgs = Organization.objects.all()
    available_orgs = dumps([{'label':o.title, 'value':o.pk} for o in available_orgs.filter(active=True).order_by("title")])

    #rdict = {'object': page_app, 'members': organizations, 'media_path': settings.MEDIA_URL, 'base_url': base_url, 'direct_link': direct_link, 'search_form': search_form, 'form' : form, 'center': center_map, 'available_locations': available_locations, 'search_form_template': search_form_template, 'mode': mode}
    rdict = {'object': page_app, 'members': orgs_page, 'media_path': settings.MEDIA_URL, 'base_url': base_url, 'direct_link': direct_link, 'search_form': search_form, 'form' : form, 'center': center_map, 'available_locations': available_locations, 'available_orgs': available_orgs, 'search_form_template': search_form_template, 'mode': mode, 'get_params': get_params.urlencode(), 'is_project': is_project}

    return rdict

    
def get_list_org_to_keep(organizations, activity):    
    tab_keep = []
    for org in organizations:
        for o in org.offer_set.all():
            parent = get_parent_activity_leve_0(o.activity)
            if parent == activity.label:
                tab_keep.append(org.pk)
    return tab_keep
    
def get_parent_activity_leve_0(activity):
    if activity.parent:
        return get_parent_activity_leve_0(activity.parent)
    else:
        return activity.label
    
def detail_view(request, page_app, pk):
    # check rights    
    #can_edit, can_add = get_rights(request)
    
    base_url = u'%s' % (page_app.get_absolute_url())
    member = get_object_or_404(Organization, pk=pk)
    imgs = member.document_set.filter(type__name='Galerie')
    docs = member.document_set.exclude(type__name='Galerie')
    
    is_project = is_obj_project(page_app)
    
    relationship_queryset = Relation.objects.filter(source=member)
    
    # check if openings
    openings = False
    for l in member.located.all():
        if l.opening:
            openings = True

    
    return render_view('page_members/detail.html',
                       { 'member':  member, 'imgs': imgs, 'docs': docs, 'media_path': settings.MEDIA_URL , 'base_url': base_url, 'openings': openings, 'relationship_queryset': relationship_queryset, 'is_project': is_project},
                       MEDIAS,
                       context_instance=RequestContext(request))
                       
def add_view(request, page_app, member_id=None):
    # check rights    
    #can_edit, can_add = get_rights(request,member_id)

    is_project = is_obj_project(page_app)
    
    if request.user.is_authenticated():
        center_map = settings.COOP_MAP_DEFAULT_CENTER
        OfferFormSet = inlineformset_factory(Organization, Offer, exclude=['technical_means', 'workforce', 'practical_modalities'], form=CustomOfferForm, extra=1)
        DocFormSet = generic_inlineformset_factory(Document, form=DocumentForm, extra=1)
        RelationFormSet = inlineformset_factory(Organization, Relation, exclude=['reltype'], fk_name='source', form=CustomRelationForm, extra=1)
        ContactFormSet = generic_inlineformset_factory(Contact, exclude=['active','sites'], extra=1)
        LocatedFormSet = generic_inlineformset_factory(Located, extra=1, form=CustomLocatedForm)
        #ReferenceFormSet = inlineformset_factory(Organization, Reference, extra=1)
        #EngagementFormSet = inlineformset_factory(Organization, Engagement,exclude=['active','sites'], extra=1)
        #MembersFormSet = inlineformset_factory(Organization, Person, extra=1)

        if member_id:
            # update
            mode = 'update'
            member = get_object_or_404(Organization, pk=member_id)
            base_url = u'%sp/member_edit/%s' % (page_app.get_absolute_url(),member_id)
            delete_url = u'%sp/member_delete/%s' % (page_app.get_absolute_url(),member_id)

        else :
            # new
            mode = 'add'
            base_url = u'%sp/member_add' % (page_app.get_absolute_url())
            delete_url = ""
            member = Organization()        
        
        if request.method == 'POST': # If the form has been submitted
        
            # TODO: auto fill :
            #correspondence
            #transmission
            #transmission_date
            #authors
            #validation
            
            form = PartialMemberForm(request.POST, request.FILES, instance = member)
            offerFormset = OfferFormSet(request.POST, request.FILES, prefix='offer', instance=member)            
            docFormset = DocFormSet(request.POST, request.FILES, prefix='doc', instance=member)
            #referenceFormset = ReferenceFormSet(prefix='ref', instance=member)    
            relationFormset = RelationFormSet(request.POST, request.FILES, prefix='rel', instance=member)    
            #engagementFormset = EngagementFormSet(request.POST, request.FILES, prefix='eng', instance=member)
            #membersFormset = MembersFormSet(request.POST, request.FILES, prefix='member', instance=member)
            contactFormset = ContactFormSet(request.POST, request.FILES, prefix='contact', instance=member)
            locatedFormset = LocatedFormSet(request.POST, request.FILES, prefix='located', instance=member)
            
            if form.is_valid() and docFormset.is_valid() and offerFormset.is_valid() and relationFormset.is_valid() and contactFormset.is_valid() and locatedFormset.is_valid():
                member = form.save()
                member.is_project = is_project
                member.save()
                docFormset.save()
                offerFormset.save()
                relationFormset.save()
                #engagementFormset.save()
                contactFormset.save()
                locatedFormset.save()                
                
                base_url = u'%s' % (page_app.get_absolute_url())
                rdict = {'base_url': base_url, 'member_id': member.pk, 'is_project': is_project, 'mode': mode}
                return render_view('page_members/add_success.html',
                                rdict,
                                MEDIAS,
                                context_instance=RequestContext(request))
        else:
            if member_id:
                # no extra formset if already some objects
                if member.offer_set.all().count() > 0:
                    OfferFormSet.extra = 0
                if member.document_set.all().count() > 0:
                    DocFormSet.extra = 0
                if member.relations.all().count() > 0:
                    RelationFormSet.extra = 0
                if member.contacts.all().count() > 0:
                    ContactFormSet.extra = 0
                if member.located.all().count() > 0:                    
                    LocatedFormSet.extra = 0
            else:
                OfferFormSet.extra = 1
                DocFormSet.extra = 1
                RelationFormSet.extra = 1
                ContactFormSet.extra = 1
                LocatedFormSet.extra = 1
                
            form = PartialMemberForm(instance=member) # An empty form
            offerFormset = OfferFormSet(instance=member, prefix='offer')
            docFormset = DocFormSet(instance=member, prefix='doc')
            relationFormset = RelationFormSet(instance=member, prefix='rel')
            contactFormset = ContactFormSet(instance=member, prefix='contact')
            locatedFormset = LocatedFormSet(instance=member, prefix='located')
            #referenceFormset = ReferenceFormSet(instance=member, prefix='ref')
            #engagementFormset = EngagementFormSet(instance=member, prefix='eng')
            #membersFormset = MembersFormSet(prefix='member')
        
        rdict = {'media_path': settings.MEDIA_URL, 'base_url': base_url, 'delete_url': delete_url, 'form': form, 'offer_form': offerFormset, 'doc_form': docFormset, 'rel_form': relationFormset,  'contact_form': contactFormset, 'center': center_map, 'located_form': locatedFormset, 'mode': mode, 'is_project' : is_project}
        return render_view('page_members/add.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request))
    else:
        return render_view('page_members/forbidden.html')
  

def delete_view(request, page_app, member_id):
    # check rights    
    can_edit, can_add = get_rights(request, member_id)
    if can_edit :
        u = Organization.objects.get(pk=member_id).delete()
        base_url = u'%s' % (page_app.get_absolute_url())
        rdict = {'base_url': base_url}
        return render_view('page_members/delete_success.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request))
    else:
        return render_view('page_members/forbidden.html')

def is_obj_project(page_app):
    if page_app.get_absolute_url() == settings.COOP_MEMBER_ORGANIZATIONS_URL:
        return False
    if page_app.get_absolute_url() == settings.COOP_MEMBER_PROJECTS_URL:
        return True

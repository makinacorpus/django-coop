# -*- coding: utf-8 -*-

from django.template import RequestContext
from ionyweb.website.rendering.utils import render_view

from coop_local.models import Organization, Offer, Document, Reference, Relation, Engagement, Person, Contact

from django.conf import settings

from django.shortcuts import get_object_or_404

from ionyweb.website.rendering.medias import CSSMedia

from .forms import PageApp_MembersForm, PartialMemberForm

from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.contrib.contenttypes.generic import generic_inlineformset_factory

from django.contrib.gis import geos
from coop_local.models import Location, Area

from coop.base_models import Located

from django.utils.simplejson import dumps

from math import pi


MEDIAS = (
    CSSMedia('page_members.css'),
    )

def index_view(request, page_app):    
    rdict = filter_data(request, page_app)
    return render_view('page_members/index.html',
                       rdict,
                       MEDIAS,
                       context_instance=RequestContext(request))                           


def carto_view(request, page_app):
    rdict = filter_data(request, page_app)    
    return render_view('page_members/index_carto.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request)) 

def filter_data(request, page_app):
    # check rights    
    can_edit, can_add = get_rights(request)
    
    if page_app.type != "":
        organizations = Organization.objects.filter(category__label=page_app.type)
    else:
        organizations = Organization.objects.all()
            
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
    
    
    if request.method == 'POST': # If the form has been submitted
        form = PageApp_MembersForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['free_search']:
                organizations = organizations.filter(Q(title__icontains=form.cleaned_data['free_search']) | Q(description__icontains=form.cleaned_data['free_search']))

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
                organizations = organizations.filter(Q(located__location__in=possible_locations))
                

            if form.cleaned_data['thematic'] or form.cleaned_data['thematic2']:
                organizations = organizations.filter(Q(transverse_themes=form.cleaned_data['thematic']) | Q(transverse_themes=form.cleaned_data['thematic2']))

            if form.cleaned_data['activity'] or form.cleaned_data['activity2']:
                activity = form.cleaned_data['activity']
                activity2 = form.cleaned_data['activity2']
                
                #TODO !!
                #print activity
                #print Organization.objects.filter(activity__parent=activity)
                #for o in Organization.objects.all():
                    #print o.activity
                    #if o.activity:
                        #print "Parent: %s" % (o.activity.parent)
                        #if o.activity.parent:
                            #print o.activity.parent.parent
                            
                organizations = organizations.filter(Q(activity=activity) | Q(activity=activity2)
                                        | Q(activity__parent=activity) | Q(activity__parent=activity2))

                
            if form.cleaned_data['statut'] and form.cleaned_data['statut2']:
                organizations = organizations.filter(Q(legal_status=form.cleaned_data['statut']) | Q(legal_status=form.cleaned_data['statut2']))
            
    else:
        form = PageApp_MembersForm(initial={'location_buffer': '10'}) # An empty form
    
    
    # Get available locations for autocomplete
    available_locations = dumps([{'label':area.label, 'value':area.pk} for area in Area.objects.all().order_by('label')])
    
    rdict = {'object': page_app, 'members': organizations, 'media_path': settings.MEDIA_URL, 'base_url': base_url, 'direct_link': direct_link, 'search_form': search_form, 'form' : form, 'center': center_map, 'available_locations': available_locations, 'search_form_template': search_form_template, 'can_edit': can_edit}

    return rdict
    
    
def detail_view(request, page_app, pk):
    # check rights    
    can_edit, can_add = get_rights(request)
    
    base_url = u'%s' % (page_app.get_absolute_url())
    member = get_object_or_404(Organization, pk=pk)
    imgs = Document.objects.all().filter(organization=member, type__name='Galerie')
    docs = Document.objects.all().filter(~Q(type__name='Galerie'), organization=member )
    return render_view('page_members/detail.html',
                       { 'member':  member, 'imgs': imgs, 'docs': docs, 'media_path': settings.MEDIA_URL , 'base_url': base_url, 'can_edit': can_edit},
                       MEDIAS,
                       context_instance=RequestContext(request))
                       
def add_view(request, page_app, member_id=None):
    # check rights    
    can_edit, can_add = get_rights(request,member_id)


    if request.user.is_authenticated():
        center_map = settings.COOP_MAP_DEFAULT_CENTER
        OfferFormSet = inlineformset_factory(Organization, Offer, extra=1)
        DocFormSet = inlineformset_factory(Organization, Document, extra=1)
        #ReferenceFormSet = inlineformset_factory(Organization, Reference, extra=1)
        #RelationFormSet = inlineformset_factory(Organization, Relation, form=PartialRelationForm, fk_name='source', extra=1)
        RelationFormSet = inlineformset_factory(Organization, Relation, exclude=['reltype'], fk_name='source', extra=1)
        EngagementFormSet = inlineformset_factory(Organization, Engagement,exclude=['active','sites'], extra=1)
        #MembersFormSet = inlineformset_factory(Organization, Person, extra=1)
        #ContactFormSet = generic_inlineformset_factory(Organization, Contact, extra=1)
        ContactFormSet = generic_inlineformset_factory(Contact, exclude=['active','sites'], extra=1)
        #ContactFormSet = generic_inlineformset_factory(Contact, Organization, extra=1, ct_field='content_type')
        #LocatedFormSet = inlineformset_factory(Organization, Located, extra=1)
        LocatedFormSet = generic_inlineformset_factory(Located, extra=1)

        if member_id:
            # update
            mode = 'update'
            member = get_object_or_404(Organization, pk=member_id)
            base_url = u'%sp/member_edit/%s' % (page_app.get_absolute_url(),member_id)

        else :
            # new
            mode = 'add'
            base_url = u'%sp/member_add' % (page_app.get_absolute_url())
            member = Organization()        
        
        if request.method == 'POST': # If the form has been submitted
        
            if page_app.get_absolute_url() == settings.COOP_MEMBER_ORGANIZATIONS_URL:
                member.is_project = False
            if page_app.get_absolute_url() == settings.COOP_MEMBER_PROJECTS_URL:
                member.is_project = True

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
            engagementFormset = EngagementFormSet(request.POST, request.FILES, prefix='eng', instance=member)
            #membersFormset = MembersFormSet(request.POST, request.FILES, prefix='member', instance=member)
            contactFormset = ContactFormSet(request.POST, request.FILES, prefix='contact', instance=member)
            locatedFormset = LocatedFormSet(request.POST, request.FILES, prefix='located', instance=member)
            
            if form.is_valid() and docFormset.is_valid() and offerFormset.is_valid() and relationFormset.is_valid() and engagementFormset.is_valid() and contactFormset.is_valid() and locatedFormset.is_valid():
                member = form.save()
                docFormset.save()
                offerFormset.save()
                relationFormset.save()
                engagementFormset.save()
                contactFormset.save()
                locatedFormset.save()
                base_url = u'%s' % (page_app.get_absolute_url())
                rdict = {'base_url': base_url, 'member_id': member.pk}
                return render_view('page_members/add_success.html',
                                rdict,
                                MEDIAS,
                                context_instance=RequestContext(request))
        else:
            form = PartialMemberForm(instance=member) # An empty form
            offerFormset = OfferFormSet(instance=member, prefix='offer')
            docFormset = DocFormSet(instance=member, prefix='doc')
            #referenceFormset = ReferenceFormSet(instance=member, prefix='ref')
            relationFormset = RelationFormSet(instance=member, prefix='rel')
            engagementFormset = EngagementFormSet(instance=member, prefix='eng')
            #membersFormset = MembersFormSet(prefix='member')
            contactFormset = ContactFormSet(instance=member, prefix='contact')
            locatedFormset = LocatedFormSet(instance=member, prefix='located')
        
        rdict = {'media_path': settings.MEDIA_URL, 'base_url': base_url, 'form': form, 'offer_form': offerFormset, 'doc_form': docFormset, 'rel_form': relationFormset, 'engagement_form': engagementFormset, 'contact_form': contactFormset, 'center': center_map, 'located_form': locatedFormset, 'mode': mode}
        return render_view('page_members/add.html',
                        rdict,
                        MEDIAS,
                        context_instance=RequestContext(request))
    else:
        return render_view('page_members/forbidden.html')

        
def get_rights(request, member_id=None): 
    can_edit = False
    can_add = False
    
    if request.user.is_superuser:
        can_edit = True
        can_add = True
    else:
        if request.user.is_authenticated():
            try:
                pes_user = Person.objects.get(user=request.user)
            except Person.DoesNotExist:
                pes_user = None
   
            if pes_user :
                if member_id:
                    #engagement = get_object_or_404(Engagement, person_id=pes_user.pk, organization_id=member_id)
                    try:
                        engagement = Engagement.objects.get(person_id=pes_user.pk, organization_id=member_id)
                    except Engagement.DoesNotExist:
                        engagement = None
                else:
                    #engagement = get_object_or_404(Engagement, person_id=pes_user.pk)
                    try:
                        engagement = Engagement.objects.get(person_id=pes_user.pk)
                    except Engagement.DoesNotExist:
                        engagement = None

                if engagement and engagement.org_admin == True:
                    can_edit = True
            
    return can_edit, can_add

    

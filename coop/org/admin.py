# -*- coding:utf-8 -*-
from django.contrib import admin
from django import forms
from django.conf import settings

from django.db.models.loading import get_model
from django.utils.translation import ugettext_lazy as _
from coop.utils.autocomplete_admin import FkAutocompleteAdmin, InlineAutocompleteAdmin, GenericInlineAutocompleteAdmin
from coop_local.models import Contact, Person, Location, ActivityNomenclature
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from django.contrib.admin.widgets import AdminURLFieldWidget
from django.db.models import URLField, ManyToManyField
from django.utils.safestring import mark_safe
from sorl.thumbnail.admin import AdminImageMixin
from tinymce.widgets import AdminTinyMCE

from chosen import widgets as chosenwidgets
from selectable.forms import AutoCompleteSelectWidget
from mptt.admin import MPTTModelAdmin

from coop.utils.autocomplete_admin import AutoCompleteSelectEditWidget, AutoComboboxSelectEditWidget
from selectable.base import ModelLookup
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from selectable.forms import AutoCompleteSelectMultipleWidget
from django.core.urlresolvers import reverse
from selectable.registry import registry
from selectable.exceptions import LookupAlreadyRegistered
from django.conf.urls.defaults import patterns, url
from django.contrib.admin.templatetags.admin_static import static
from django.shortcuts import render
from django.contrib.contenttypes.generic import generic_inlineformset_factory

if "coop.exchange" in settings.INSTALLED_APPS:
    from coop.exchange.admin import ExchangeInline

if "coop_geo" in settings.INSTALLED_APPS:
    from coop_geo.admin import LocatedInline, AreaInline


class LocationLookup(ModelLookup):
    model = Location
    search_fields = ('label__icontains', 'adr1__icontains', 'adr2__icontains', 'zipcode__icontains', 'city__icontains')

    def get_query(self, request, term):
        print term
        results = super(LocationLookup, self).get_query(request, term)
        print results
        if 'pks' in request.GET:
            print request.GET['pks']
            if request.GET['pks']:
                pks = request.GET['pks'].split(',')
                results = results.filter(pk__in=pks)
            else:
                results = results.none()
            print results
        return results


class AreaLookup(ModelLookup):
    model = get_model('coop_local', 'Area')
    search_fields = ('label__icontains', 'reference__icontains')


class ActivityLookup(ModelLookup):
    model = ActivityNomenclature
    search_fields = ('path__icontains', )
    filters = {'level': 2}


try:
    registry.register(LocationLookup)
except LookupAlreadyRegistered:
    pass
try:
    registry.register(AreaLookup)
except LookupAlreadyRegistered:
    pass
try:
    registry.register(ActivityLookup)
except LookupAlreadyRegistered:
    pass


class URLFieldWidget(AdminURLFieldWidget):
    def render(self, name, value, attrs=None):
        widget = super(URLFieldWidget, self).render(name, value, attrs)
        return mark_safe(u'%s&nbsp;&nbsp;<a href="#" onclick="window.'
                         u'open(document.getElementById(\'%s\')'
                         u'.value);return false;" class="btn btn-mini"/>Afficher dans une nouvelle fenêtre</a>' % (widget, attrs['id']))


class ReferenceInline(InlineAutocompleteAdmin):

    model = get_model('coop_local', 'Reference')
    verbose_name = _(u'reference')
    verbose_name_plural = _(u'references')
    fields = ('customer', 'from_year', 'to_year', 'services')
    extra = 1


def make_contact_form(pks, admin_site, request):
    class ContactForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(ContactForm, self).__init__(*args, **kwargs)
            location_rel = Contact._meta.get_field_by_name('location')[0].rel
            medium_rel = Contact._meta.get_field_by_name('contact_medium')[0].rel
            self.fields['location'].widget = AutoComboboxSelectEditWidget(location_rel, admin_site, LocationLookup)
            if pks is not None:
                self.fields['location'].widget.update_query_parameters({'pks': ','.join(map(str, pks))})
            self.fields['location'].widget.choices = None
            self.fields['location'].widget = RelatedFieldWidgetWrapper(self.fields['location'].widget, location_rel, admin_site, can_add_related=False)
            self.fields['contact_medium'].widget = RelatedFieldWidgetWrapper(self.fields['contact_medium'].widget, medium_rel, admin_site, can_add_related=False)
        class Meta:
            model = Contact
            fields = ('contact_medium', 'content', 'details', 'location', 'display')
    return ContactForm


class ContactInline(GenericInlineAutocompleteAdmin):
    model = get_model('coop_local', 'Contact')
    verbose_name = _(u'Contact information')
    verbose_name_plural = _(u'Contact informations')
    fields = ('contact_medium', 'content', 'details', 'location', 'display')
    extra = 1
    def get_formset(self, request, obj=None, **kwargs):
        if not obj:
            pks = None
        elif isinstance(obj, get_model('coop_local', 'Organization')):
            pks = Location.objects.filter(located__organization=obj).values_list('pk', flat=True)
        elif isinstance(obj, Person):
            pks = [obj.location.pk] if obj.location else []
            pks += Location.objects.filter(located__organization__members=obj).values_list('pk', flat=True)
        else:
            pks = None
        return generic_inlineformset_factory(Contact, form=make_contact_form(pks, self.admin_site, request))


class EngagementInline(InlineAutocompleteAdmin):
    model = get_model('coop_local', 'Engagement')
    verbose_name = _(u'Member')
    verbose_name_plural = _(u'Members')
    fields = ('person', 'role', 'role_detail', 'org_admin', 'engagement_display')

    related_search_fields = {
        'person': ('last_name', 'first_name', 'email', 'structure', 'username'),
        'role': ('label', )
    }
    related_combobox = ('role', )
    extra = 2


class RelationInline(InlineAutocompleteAdmin):
    model = get_model('coop_local', 'Relation')
    fk_name = 'source'
    readonly_fields = ('created',)
    fields = ('relation_type', 'target', 'created')
    related_search_fields = {'target': ('title', 'subtitle', 'acronym',), }
    extra = 1


class OrgInline(InlineAutocompleteAdmin):
    model = get_model('coop_local', 'Engagement')
    verbose_name = _(u'Engagement')
    verbose_name_plural = _(u'Engagements')
    fields = ('organization', 'role', 'role_detail', 'engagement_display')

    related_search_fields = {
        'organization': ('title', 'acronym',),
        'role': ('label', ),
    }
    related_combobox = ('role', )
    extra = 1


class RoleAdmin(admin.ModelAdmin):
    list_display = ('label', 'category')
    list_editable = ('category',)


class ActivityWidget(AutoCompleteSelectEditWidget):

    def render(self, name, value, attrs=None):
        markup = super(ActivityWidget, self).render(name, value, attrs)
        related_url = reverse('admin:coop_local_offer_activity_list', current_app=self.admin_site.name)
        markup += u'&nbsp;<a href="%s" class="activity-lookup" id="lookup_id_%s" onclick="return showActivityLookupPopup(this);">' % (related_url, name)
        markup += u'<img src="%s" width="16" height="16"></a>' % static('admin/img/selector-search.gif')
        return mark_safe(markup)


def make_offer_form(admin_site, request):
    class OfferAdminForm(forms.ModelForm):
        class Meta:
            model = get_model('coop_local', 'Offer')
        def __init__(self, *args, **kwargs):
            super(OfferAdminForm, self).__init__(*args, **kwargs)
            activity_rel = get_model('coop_local', 'Offer')._meta.get_field_by_name('activity')[0].rel
            related_modeladmin = admin_site._registry.get(activity_rel.to)
            can_change_related = bool(related_modeladmin and
                related_modeladmin.has_change_permission(request))
            can_add_related = bool(related_modeladmin and
                related_modeladmin.has_add_permission(request))
            activity_widget = ActivityWidget(activity_rel, admin_site, ActivityLookup, can_change_related=can_change_related)
            activity_widget.choices = None
            self.fields['activity'].widget = RelatedFieldWidgetWrapper(activity_widget, activity_rel, admin_site, can_add_related=can_add_related)
            targets_rel = get_model('coop_local', 'Offer')._meta.get_field_by_name('targets')[0].rel
            targets_widget = forms.CheckboxSelectMultiple(attrs={'class': 'multiple_checkboxes'}, choices=self.fields['targets'].choices)
            self.fields['targets'].widget = RelatedFieldWidgetWrapper(targets_widget, targets_rel, admin_site, can_add_related=False)
            #area_rel = get_model('coop_local', 'Offer')._meta.get_field_by_name('area')[0].rel
            self.fields['area'].widget = AutoCompleteSelectMultipleWidget(AreaLookup)
    return OfferAdminForm


class OfferInline(admin.StackedInline):

    model = get_model('coop_local', 'Offer')
    verbose_name = _(u'offer')
    verbose_name_plural = _(u'offers')
    formfield_overrides = {ManyToManyField: {'widget': forms.CheckboxSelectMultiple(attrs={'class':'multiple_checkboxes'})}}

    def get_formset(self, request, obj=None, **kwargs):
        return forms.models.inlineformset_factory(get_model('coop_local', 'Organization'), get_model('coop_local', 'Offer'), form=make_offer_form(self.admin_site, request), extra=1)


class DocumentInline(InlineAutocompleteAdmin):

    model = get_model('coop_local', 'Document')
    verbose_name = _(u'document')
    verbose_name_plural = _(u'documents')
    extra = 1


class GuarantyAdmin(AdminImageMixin, admin.ModelAdmin):

    list_display = ('logo_list_display', 'type', 'name')
    list_display_links = ('name', )
    list_filter = ('type', )
    search_fields = ('type', 'name')


class OrganizationAdminForm(forms.ModelForm):
    description = forms.CharField(widget=AdminTinyMCE(attrs={'cols': 80, 'rows': 60}), required=False)

    class Meta:
        model = get_model('coop_local', 'Organization')
        widgets = {
            'category': chosenwidgets.ChosenSelectMultiple(),
            'sites': chosenwidgets.ChosenSelectMultiple(),
            'guaranties': chosenwidgets.ChosenSelectMultiple(),
            'authors': chosenwidgets.ChosenSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super(OrganizationAdminForm, self).__init__(*args, **kwargs)
        engagements = self.instance.engagement_set.all()
        members_id = engagements.values_list('person_id', flat=True)
        org_contacts = Contact.objects.filter(
            Q(content_type=ContentType.objects.get(model='organization'), object_id=self.instance.id)
          | Q(content_type=ContentType.objects.get(model='person'), object_id__in=members_id)
            )
        phone_categories = [1, 2]
        self.fields['pref_email'].queryset = org_contacts.filter(contact_medium_id=8)
        self.fields['pref_phone'].queryset = org_contacts.filter(contact_medium_id__in=phone_categories)
        self.fields['category'].help_text = None
        if 'sites' in self.fields:
            self.fields['sites'].help_text = None


        member_locations_id = [m.location.id for m in
            Person.objects.filter(id__in=members_id).exclude(location=None)]  # limit SQL to location field

        self.fields['pref_address'].queryset = Location.objects.filter(
            Q(id__in=self.instance.located.all().values_list('location_id', flat=True))
          | Q(id__in=member_locations_id)
            )

        for field_name in ('workforce', ):
            self.fields[field_name].localize = True



def create_action(category):
    def add_cat(modeladmin, request, queryset):
        for obj in queryset:
            obj.category.add(category)
    name = "cat_%s" % (category.slug,)
    return (name, (add_cat, name, _(u'Add to the "%s" category') % (category,)))


class OrganizationAdmin(AdminImageMixin, FkAutocompleteAdmin):
    change_form_template = 'admin/coop_local/organization/tabbed_change_form.html'
    form = OrganizationAdminForm
    list_display = ['logo_list_display', 'label', 'active', 'has_description', 'has_location']
    list_display_links = ['label', ]
    search_fields = ['title', 'acronym', 'acronym', 'description']
    list_filter = ['active', 'category']
    readonly_fields = ['creation', 'modification']
    #actions_on_top = True
    #actions_on_bottom = True
    #save_on_top = True
    #filter_horizontal = ('category',)
    list_per_page = 10
    list_select_related = True
    #read_only_fields = ['created','modified']
    ordering = ('title',)
    related_search_fields = {'activity': ('path',), }
    formfield_overrides = {
        URLField: {'widget': URLFieldWidget},
        ManyToManyField: {'widget': forms.CheckboxSelectMultiple}
    }

    if "coop.exchange" in settings.INSTALLED_APPS:
        inlines = [ ContactInline,
                        EngagementInline,
                        ExchangeInline,
                        RelationInline,
                        LocatedInline,
                        AreaInline,
                        OfferInline,
                        DocumentInline,
                        ReferenceInline,
                        ]
    else:
        inlines = [ ContactInline,
                    EngagementInline,
                    LocatedInline,
                    OfferInline,
                    DocumentInline,
                    ReferenceInline,
                    ]

    # grace au patch
    # https://code.djangoproject.com/ticket/17856
    # https://github.com/django/django/blob/master/django/contrib/admin/options.py#L346
    # def get_inline_instances(self, request, obj):
    #     inline_instances = []

    #     for inline_class in self.inlines:
    #         if inline_class.model == get_model('coop_local', 'Exchange'):
    #             inline = inline_class(self.model, self.admin_site, obj=obj)
    #         else:
    #             inline = inline_class(self.model, self.admin_site)
    #         inline_instances.append(inline)
    #     return inline_instances

    fieldsets = (
        ('Identité', {
            'fields': ['logo', 'title', ('acronym', 'pref_label'), ('birth', 'active',),
                        'web', 'is_project', 'legal_status']
            }),
        ('Description', {
            'fields': ['short_description', 'description', 'category', 'activity', 'transverse_themes']  # 'tags', ]
            }),
        (_(u'Economic info'), {
            'fields': [('annual_revenue', 'workforce')]
            }),
        (_(u'Management'), {
            'fields': ['creation', 'modification', 'status', 'correspondence', 'transmission',
                       'transmission_date', 'authors', 'validation']
            }),
        ('Préférences', {
            #'classes': ('collapse',),
            'fields': ['pref_email', 'pref_phone', 'pref_address', 'notes',]
            }),
        (_(u'Testimony'), {
            'fields': ['testimony',]
            }),
        (_(u'Guaranties'), {
            'fields': ['guaranties']
            }),
    )

    if settings.COOP_USE_SITES:
        fieldsets[0][1]['fields'].insert(0, 'sites')
        list_filter.append('sites')

    def get_actions(self, request):
        myactions = dict(create_action(s) for s in get_model('coop_local', 'OrganizationCategory').objects.all())
        return dict(myactions, **super(OrganizationAdmin, self).get_actions(request))  # merging two dicts
        #list_display = ['my_image_thumb', 'my_other_field1', 'my_other_field2', ] ???

    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._obj_ = obj
        return super(OrganizationAdmin, self).get_form(request, obj, **kwargs)

    def get_urls(self):
        urls = super(OrganizationAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^activity_list/$', self.activity_list_view, name='coop_local_offer_activity_list')
        )
        return my_urls + urls

    def activity_list_view(self, request):
        activities = ActivityNomenclature.objects.all()
        return render(request, 'admin/activity_list.html', {'activities': activities, 'is_popup': True})

    def save_related(self, request, form, formsets, change):
        super(OrganizationAdmin, self).save_related(request, form, formsets, change)
        if not change:
            form.instance.authors.add(request.user)

    class Media:
        js = ('/static/js/admin_customize.js',)


class ActivityNomenclatureAdmin(MPTTModelAdmin, FkAutocompleteAdmin):

    related_search_fields = {'avise': ('label',), 'parent': ('path',)}
    mptt_indent_field = 'label'
    mptt_level_indent = 50
    list_display = ('label', )

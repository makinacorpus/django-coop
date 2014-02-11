# -*- coding:utf-8 -*-

from django.conf import settings
from django.contrib import admin
from django import forms
from coop_local.models import Event, EventCategory, Calendar, Occurrence, Dated
from coop.utils.autocomplete_admin import FkAutocompleteAdmin, InlineAutocompleteAdmin, NoLookupsFkAutocompleteAdmin
from coop_geo.admin import LocatedInline
from django.contrib.contenttypes.generic import GenericTabularInline
from django.utils.translation import ugettext_lazy as _
from coop.agenda.forms import SingleOccurrenceForm
from django.db.models.loading import get_model
from chosen import widgets as chosenwidgets

#from genericadmin.admin import GenericAdminModelAdmin
# GenericStackedInline or GenericTabularInline
# on fera le lien generique depuis l'objet en question si besoin (article, événement)


class EventCategoryAdmin(admin.ModelAdmin):
    list_display = ('label',)


class OccurrenceInline(admin.StackedInline):
    #form = SingleOccurrenceForm
    verbose_name = _(u'Date')
    verbose_name_plural = _(u'Dates')
    model = Occurrence
    extra = 1


class EventAdminForm(forms.ModelForm):
    class Meta:
        model = get_model('coop_local', 'Event')
        widgets = {'sites': chosenwidgets.ChosenSelectMultiple(),
                   'category': chosenwidgets.ChosenSelectMultiple()
                   }

    def __init__(self, *args, **kwargs):
        # initial = {
        #     'category': 1, 
        #     'calendar': 1 
        #     }
        # if not kwargs.has_key('initial'):
        # #     kwargs['initial'].update(initial)
        # # else:
        #     kwargs['initial'] = initial
        # Initializing form only after you have set initial dict
        super(EventAdminForm, self).__init__(*args, **kwargs)
        self.fields['calendar'].initial = Calendar.objects.get(id=1)
        self.fields['category'].help_text = None
        # self.fields['category'].initial = EventCategory.objects.get(id=1)
        if 'sites' in self.fields:
            self.fields['sites'].help_text = None


class EventAdmin(NoLookupsFkAutocompleteAdmin):
    change_form_template = 'admintools_bootstrap/tabbed_change_form.html'
    form = EventAdminForm
    list_display = ('title', 'time_str', 'description', 'active')
    list_filter = ('status', 'category', 'active')
    search_fields = ('title', 'description')
    related_search_fields = {'person': ('last_name', 'first_name',
                                        'email', 'structure', 'username'),
                            'organization': ('title', 'acronym',  'description'),
                            'location': ('label', 'adr1', 'adr2', 'zipcode', 'city'),
    }
    fieldsets = [['Description', {'fields': ['title', 'description',
        'category', ('calendar', 'active'),
        'organization', 'remote_organization_label', 'remote_organization_uri',
        'person', 'remote_person_label', 'remote_person_uri',
        'location', 'remote_location_label', 'remote_location_uri', 'status'
      ]}],
    ]
    ordering = ('-occurrence__start_time', )

    if "coop_tag" in settings.INSTALLED_APPS:
        fieldsets[0][1]['fields'].insert(2, 'tags')

    if settings.COOP_USE_SITES:
        fieldsets[0][1]['fields'].insert(0, 'sites')

    inlines = [OccurrenceInline]

    def time_str(self, obj):
        try:
            occurrence = obj.occurrence_set.order_by('start_time')[0]
        except IndexError:
            return ''
        return occurrence.start_time.strftime('%d/%m/%Y')
    time_str.short_description = 'Date'
    time_str.allow_tags = True
    time_str.admin_order_field = 'occurrence__start_time'    
    
admin.site.register(Event, EventAdmin)
admin.site.register(EventCategory, EventCategoryAdmin)
admin.site.register(Calendar)


class DatedInline(GenericTabularInline, InlineAutocompleteAdmin):
    verbose_name = _(u'Date')
    verbose_name_plural = _(u'Dates')
    model = Dated
    related_search_fields = {'event': ('title', 'description', 'slug'), }
    extra = 1

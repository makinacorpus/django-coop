# -*- coding: utf-8 -*-

import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from .models import PageApp_CoopAgenda
from django.utils.translation import ugettext, ugettext_lazy as _
from coop.agenda.forms import EventForm, MultipleOccurrenceForm, SingleOccurrenceForm

from coop.base_models import ActivityNomenclature, TransverseTheme
from coop_local.models import Event, Occurrence

class PageApp_CoopAgendaForm(ModuloModelForm):

    location = forms.CharField(required=False, label=_('Location'))
    location_id = forms.IntegerField(required=False)
    location_buffer = forms.IntegerField(required=False, label=_('Location buffer'))
    free_search = forms.CharField(required=False, label=_('Free search'))
    
    activity = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.filter(parent__isnull=True).order_by('label'),required=False, label=_('Activity'))
    activity2 = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.filter(parent__isnull=True).order_by('label'),required=False, label=_('Activity'))
    
    thematic = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))
    thematic2 = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))
     
    organization = forms.CharField(required=False, label=_('Organization'))
    start_date = forms.DateField(required=False, label=_('Start date'))
    end_date = forms.DateField(required=False, label=_('End date'))
    type = forms.CharField(required=False, label=_('Type'))
    
    class Meta:
        model = PageApp_CoopAgenda

class PartialEventForm(EventForm):
    
    class Meta:
        model = Event
        exclude = ('calendar', 'sites', )

        
class PartialOccEventForm(SingleOccurrenceForm):
    
    class Meta:
        model = Occurrence
        #exclude = ('',)
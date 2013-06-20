# -*- coding: utf-8 -*-

import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from .models import PageApp_CoopAgenda
from django.utils.translation import ugettext, ugettext_lazy as _
from coop.agenda.forms import EventForm, MultipleOccurrenceForm, SingleOccurrenceForm

from coop.base_models import ActivityNomenclature, TransverseTheme, Document, Located
from coop_local.models import Event, Occurrence, Location
from django.conf import settings

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
    
    label = forms.CharField(required=False, label=_('Label'))
    address = forms.CharField(required=False, label=_('Address'))
    city = forms.CharField(required=False, label=_('City'))
    zipcode = forms.CharField(required=False, label=_('Zipcode'))
    point = forms.gis.PointField(required=False, label=_('Point'), widget=forms.gis.BaseOsmWidget(attrs={'map_width': 300,'map_height': 300}), null=True,srid=settings.COOP_GEO_EPSG_PROJECTION)
    
    class Meta:
        model = Event
        exclude = ('calendar', 'sites', )
        #fields = ('label', 'address', 'city', 'zipcode', 'point', 'main_location')
        
    def __init__(self, *args, **kwargs):
        super(PartialEventForm, self).__init__(*args, **kwargs)
        
        try:
            location = self.instance.location
        except Location.DoesNotExist:
            location = None

        if location :
            self.fields['label'].initial = location.label
            self.fields['address'].initial = location.adr1
            self.fields['city'].initial = location.city
            self.fields['zipcode'].initial = location.zipcode
            self.fields['point'].initial = location.point
        
    def save(self, commit=True):
        event = super(PartialEventForm, self).save(commit=False)
        
        if self.cleaned_data:
            location = self.instance.location
            if location == None:
                location = Location()

            location.label = self.cleaned_data['label']
            location.adr1 = self.cleaned_data['address']
            location.zipcode = self.cleaned_data['zipcode']
            location.city = self.cleaned_data['city']
            location.point = self.cleaned_data['point']
            if commit:
                location.save()
      
            event.location = location            
      
        if commit:
            event.save()
        return event        
        
class PartialOccEventForm(SingleOccurrenceForm):
    
    class Meta:
        model = Occurrence
        #exclude = ('',)
        
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }     
        
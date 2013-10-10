# -*- coding: utf-8 -*-

from django.utils.translation import ugettext, ugettext_lazy as _
from django.conf import settings
from django.contrib.admin import widgets as adminWidgets

import floppyforms as forms

from ionyweb.forms import ModuloModelForm
from ionyweb.widgets import DateTimePicker

from .models import PageApp_CoopAgenda
from coop.agenda.forms import EventForm, MultipleOccurrenceForm, SingleOccurrenceForm
from coop.base_models import ActivityNomenclature, TransverseTheme, Document, Located
from coop_local.models import Event, Occurrence, Location, Organization
from coop_local.widgets import CustomClearableFileInput
from coop_geo.widgets import LocationPointWidgetInline

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
    point = forms.gis.PointField(required=False, label=_('Point'), widget=LocationPointWidgetInline(attrs={'map_width': 300,'map_height': 300, 'result_height': 100}), null=True,srid=settings.COOP_GEO_EPSG_PROJECTION, help_text=_('You may point manually the location of the location'))    
    
    class Meta:
        model = Event
        exclude = ('calendar', 'sites', )
        #fields = ('label', 'address', 'city', 'zipcode', 'point', 'main_location')
        widgets = {'image' : CustomClearableFileInput(),}

        
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
        
        self.fields['activity'] = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.order_by('path'))
        self.fields['activity'].label = _('Activity')
        self.fields['active'].label = _('Show on public site')
        self.fields['organization'].label = _('Organizator')
        
        self.fields['organization'] = forms.ModelChoiceField(queryset=Organization.objects.filter(active=True, is_project=False).order_by('title'))
        self.fields['organizations'] = forms.ModelMultipleChoiceField(required=False, queryset=Organization.objects.filter(active=True, is_project=False).order_by('title'))
        
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
        
    def __init__(self, *args, **kwargs):
        super(PartialOccEventForm, self).__init__(*args, **kwargs)        
        
        self.fields['start_time'].label = _('Start date')
        self.fields['end_time'].label = _('End date')

        self.fields['start_time'].widget = DateTimePicker()
        self.fields['end_time'].widget = DateTimePicker()
        

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }     

class ReplyEventForm(forms.Form):
    title = forms.CharField(required=True, label=_('Title'))
    email = forms.EmailField(required=True, label=_('Email'))
    response = forms.CharField(required=True, label=_('Response'), widget=forms.Textarea)
        
# -*- coding: utf-8 -*-

from django.utils.translation import ugettext, ugettext_lazy as _
import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from .models import PageApp_CoopExchange

from coop.exchange.models import ETYPE, EWAY
from coop.exchange.admin import ExchangeForm
from coop_local.models import Exchange, Document, Person, Location, ExchangeMethod, Organization
from coop_local.widgets import CustomCheckboxSelectMultiple, CustomClearableFileInput
from coop.base_models import ActivityNomenclature, TransverseTheme
from extended_choices import Choices
from coop_geo.widgets import LocationPointWidgetInline
from django.conf import settings
from ionyweb.widgets import TinyMCELargeTable

EMODE = Choices(
    ('GIFT',    1,  _(u'Gift')),
    ('SWAP',   2,  _(u'Swap')),
    ('SKILL',   3,  _(u'Skill')),
    ('EUROS',    4,  _(u'Euros')),
    ('MUTUALIZATION',      5,  _(u'Mutualization')),
)

ESKILLS = Choices(
    ('VOLUNTARY',    1,  _(u'Voluntary')),
    ('TRAINING_WORK',   2,  _(u'Training work')),
    ('JOB_OFFER',   3,  _(u'Job offer')),
    ('TRAINING',    4,  _(u'Training')),
)



class PageApp_CoopExchangeForm(ModuloModelForm):

    type_exchange = forms.MultipleChoiceField(required=False, choices=EWAY, widget=CustomCheckboxSelectMultiple())

    type = forms.MultipleChoiceField(required=False, choices=ETYPE, widget=CustomCheckboxSelectMultiple())

    activity = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.filter(parent__isnull=True).order_by('label'),required=False, label=_('Activity'))
    activity2 = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.filter(parent__isnull=True).order_by('label'),required=False, label=_('Activity'))
    
    location = forms.CharField(required=False, label=_('Location'))
    location_buffer = forms.IntegerField(required=False, label=_('Location buffer'))
    location_id = forms.IntegerField(required=False)
    
    thematic = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))
    thematic2 = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))
    
    #mode = forms.MultipleChoiceField(required=False, choices=EMODE, widget=CustomCheckboxSelectMultiple())
    method = forms.ModelMultipleChoiceField(queryset=ExchangeMethod.objects.exclude(etypes__contains=3), required=False, widget=CustomCheckboxSelectMultiple())
    
    #skills = forms.MultipleChoiceField(required=False, choices=ESKILLS, widget=CustomCheckboxSelectMultiple())
    skills = forms.ModelMultipleChoiceField(queryset=ExchangeMethod.objects.filter(etypes__contains=3), required=False, widget=CustomCheckboxSelectMultiple())
    
    free_search = forms.CharField(required=False, label=_('Free search'))
    
    warranty = forms.CharField(required=False, label=_('Warranty'))
    
    organization = forms.CharField(required=False, label=_('Organization'))
    
    tags = forms.CharField(required=False, label=_('Keywords'))
    
    class Meta:
        model = PageApp_CoopExchange


class ReplyExchangeForm(forms.Form):
    title = forms.CharField(required=True, label=_('Title'))
    email = forms.EmailField(required=True, label=_('Email'))
    response = forms.CharField(required=True, label=_('Response'), widget=forms.Textarea)
    
        
class PartialExchangeForm(ExchangeForm):
    
    label = forms.CharField(required=False, label=_('Label'))
    address = forms.CharField(required=False, label=_('Address'))
    city = forms.CharField(required=False, label=_('City'))
    zipcode = forms.CharField(required=False, label=_('Zipcode'))
    point = forms.gis.PointField(required=False, label=_('Point'), widget=LocationPointWidgetInline(attrs={'map_width': 300,'map_height': 300, 'result_height': 100}), null=True,srid=settings.COOP_GEO_EPSG_PROJECTION, help_text=_('You may point manually the location of the location'))    
        
    class Meta:
        model = Exchange
        exclude = ('products', 'sites', )
        widgets = {
                'img' : CustomClearableFileInput(),
              }
        

    def __init__(self, *args, **kwargs):
        super(PartialExchangeForm, self).__init__(*args, **kwargs)
        self.fields['activity'] = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.order_by('path'))
        self.fields['person'] = forms.ModelChoiceField(queryset=Person.objects.order_by('first_name'))
        
        self.fields['description'].widget.attrs['rows'] = '15'
        self.fields['description'].widget.attrs['cols'] = '55' 
        
        self.fields['activity'].label = _("Activity")
        self.fields['person'].label = _("Person")
        self.fields['start'].label = _("Date of publication")
        
        self.fields['organization'] = forms.ModelChoiceField(queryset=Organization.objects.filter(active=True, is_project=False).order_by('title'))
        
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
        exchange = super(PartialExchangeForm, self).save(commit=False)
        
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
      
            exchange.location = location            
      
        if commit:
            exchange.save()
        return exchange        


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }        
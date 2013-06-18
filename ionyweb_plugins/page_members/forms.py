# -*- coding: utf-8 -*-


from django.db import models
import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from django.forms import ModelForm
from .models import PageApp_Members
from django.utils.translation import ugettext, ugettext_lazy as _
from extended_choices import Choices

from coop_local.models import Organization, LegalStatus
from coop.org.admin import OrganizationAdminForm, RelationInline

from coop.base_models import ActivityNomenclature, TransverseTheme
from coop_local.models import Relation, Location, Document
from coop.base_models import Located
from django.db.models.loading import get_model

from chosen import widgets as chosenwidgets

import floppyforms as forms
import models




class PageApp_MembersForm(ModelForm):

    type = forms.CharField(required=False, label=_('Type'))
    
    activity = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.filter(parent__isnull=True).order_by('label'),required=False, label=_('Activity'))
    activity2 = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.filter(parent__isnull=True).order_by('label'),required=False, label=_('Activity'))
    
    location = forms.CharField(required=False, label=_('Location'))
    location_id = forms.IntegerField(required=False)
    location_buffer = forms.IntegerField(required=False, label=_('Location buffer'))
    thematic = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))
    thematic2 = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))
    statut = forms.ModelChoiceField(queryset=LegalStatus.objects.all(), required=False)
    statut2 = forms.ModelChoiceField(queryset=LegalStatus.objects.all(), required=False)
    
    free_search = forms.CharField(required=False, label=_('Free search'))
    
    date_start = forms.DateField(required=False)
    
    class Meta:
        model = PageApp_Members
        
        
class PartialMemberForm(OrganizationAdminForm):
    class Meta:
        model = Organization
        exclude = ('members', 'secteur_fse', 'sites', 'relations', 'statut', )


class CustomLocatedForm(forms.ModelForm):
    label = forms.CharField(required=False, label=_('Label'))
    address = forms.CharField(required=False, label=_('Address'))
    city = forms.CharField(required=False, label=_('City'))
    zipcode = forms.CharField(required=False, label=_('Zipcode'))
    
    class Meta:
        model = Located

        fields = ('label', 'address', 'city', 'zipcode', 'opening', 'main_location')

    def __init__(self, *args, **kwargs):
        super(CustomLocatedForm, self).__init__(*args, **kwargs)
        
        
        try:
            location = self.instance.location
        except Location.DoesNotExist:
            location = None

        if location :
            self.fields['label'].initial = location.label
            self.fields['address'].initial = location.adr1
            self.fields['city'].initial = location.city
            self.fields['zipcode'].initial = location.zipcode
        
    def clean(self):
        cleaned_data = self.cleaned_data
        return cleaned_data
        
    def save(self, commit=True):
        located = super(CustomLocatedForm, self).save(commit=False)
        
        if self.cleaned_data:
            location = self.instance.location
            if location == None:
                location = Location()

            location.label = self.cleaned_data['label']
            location.adr1 = self.cleaned_data['address']
            location.zipcode = self.cleaned_data['zipcode']
            location.city = self.cleaned_data['city']
            if commit:
                location.save()
      
            located.location = location            
      
        if commit:
            located.save()
        return located

        
        
class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
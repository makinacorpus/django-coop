# -*- coding: utf-8 -*-


from django.db import models
import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from django.forms import ModelForm
from .models import PageApp_Members
from django.utils.translation import ugettext, ugettext_lazy as _
from extended_choices import Choices

from coop_local.models import Organization, LegalStatus
from coop.org.admin import OrganizationAdminForm

from coop.base_models import ActivityNomenclature, TransverseTheme


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
        

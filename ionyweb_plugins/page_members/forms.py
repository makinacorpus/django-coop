# -*- coding: utf-8 -*-

import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from django.forms import ModelForm
from .models import PageApp_Members
from django.utils.translation import ugettext, ugettext_lazy as _

from coop_local.models import Organization
from coop.org.admin import OrganizationAdminForm

from coop.base_models import ActivityNomenclature, TransverseTheme

class PageApp_MembersForm(ModelForm):

    type = forms.CharField(required=False, label=_('Type'))
    
    activity = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.all(),required=False, label=_('Activity'))
    
    location = forms.CharField(required=False, label=_('Location'))
    location_buffer = forms.IntegerField(required=False, label=_('Location buffer'))
    thematic = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))

    free_search = forms.CharField(required=False, label=_('Free search'))
    
    class Meta:
        model = PageApp_Members
        
        
class PartialMemberForm(OrganizationAdminForm):
    class Meta:
        model = Organization
        exclude = ('members', 'secteur_fse', 'sites', 'relations', 'statut', )
        

# -*- coding: utf-8 -*-

from django.utils.translation import ugettext, ugettext_lazy as _
import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from .models import PageApp_CoopTerritory

from coop_local.widgets import CustomCheckboxSelectMultiple, CustomClearableFileInput
from coop.base_models import ActivityNomenclature, TransverseTheme
from extended_choices import Choices

from coop_local.models import LegalStatus, Location

CONTENT_TYPES = Choices (
    ('Exchange',    1,  _(u'Exchange')),
    ('Event',   2,  _(u'Event')),
    ('Organization',   3,  _(u'Organization')),
    ('Project',    4,  _(u'Project')),
    ('Service',      5,  _(u'Service')),
)



class PageApp_CoopTerritoryForm(ModuloModelForm):

    type_content = forms.MultipleChoiceField(required=False, choices=CONTENT_TYPES, widget=CustomCheckboxSelectMultiple())

    departement = forms.ModelChoiceField(queryset=Location.objects.order_by('label'), required=False)

    country = forms.ModelChoiceField(queryset=Location.objects.order_by('label'), required=False)
    
    epci = forms.ModelChoiceField(queryset=Location.objects.order_by('label'), required=False)
    
    commune = forms.ModelChoiceField(queryset=Location.objects.order_by('label'), required=False)

    activity = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.filter(parent__isnull=True).order_by('label'),required=False, label=_('Activity'))
    activity2 = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.filter(parent__isnull=True).order_by('label'),required=False, label=_('Activity'))
    
    thematic = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))
    thematic2 = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))
    
    statut = forms.ModelChoiceField(queryset=LegalStatus.objects.all(), required=False)
    statut2 = forms.ModelChoiceField(queryset=LegalStatus.objects.all(), required=False)
    
    free_search = forms.CharField(required=False, label=_('Free search'))
    
    class Meta:
        model = PageApp_CoopTerritory
   
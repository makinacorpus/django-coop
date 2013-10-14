# -*- coding: utf-8 -*-

from django.utils.translation import ugettext, ugettext_lazy as _
import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from .models import PageApp_CoopService

from coop_local.widgets import CustomCheckboxSelectMultiple, CustomClearableFileInput
from coop.base_models import ActivityNomenclature, TransverseTheme
from extended_choices import Choices

from coop_local.models import LegalStatus, Location, Area, ExchangeMethod


class PageApp_CoopServiceForm(ModuloModelForm):

    class Meta:
        model = PageApp_CoopService
   
class PageApp_CoopServiceSearchForm(ModuloModelForm):

    activity = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.filter(parent__isnull=True).order_by('label'),required=False, label=_('Activity'))
    activity2 = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.filter(parent__isnull=True).order_by('label'),required=False, label=_('Activity'))

    location = forms.CharField(required=False, label=_('Location'))
    location_buffer = forms.IntegerField(required=False, label=_('Location buffer'))
    location_id = forms.IntegerField(required=False)

    thematic = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))
    thematic2 = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))

    method = forms.ModelMultipleChoiceField(queryset=ExchangeMethod.objects.exclude(etypes__contains=3), required=False, widget=CustomCheckboxSelectMultiple())

    free_search = forms.CharField(required=False, label=_('Free search'))

    
    class Meta:
        model = PageApp_CoopService
   
   
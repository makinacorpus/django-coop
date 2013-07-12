# -*- coding: utf-8 -*-

from django.utils.translation import ugettext, ugettext_lazy as _
import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from .models import PageApp_CoopService

from coop_local.widgets import CustomCheckboxSelectMultiple, CustomClearableFileInput
from coop.base_models import ActivityNomenclature, TransverseTheme
from extended_choices import Choices

from coop_local.models import LegalStatus, Location, Area


EMODE = Choices(
    ('GIFT',    1,  _(u'Gift')),
    ('SWAP',   2,  _(u'Swap')),
    ('SKILL',   3,  _(u'Skill')),
    ('EUROS',    4,  _(u'Euros')),
    ('MUTUALIZATION',      5,  _(u'Mutualization')),
)



class PageApp_CoopServiceForm(ModuloModelForm):

    activity = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.filter(parent__isnull=True).order_by('label'),required=False, label=_('Activity'))
    activity2 = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.filter(parent__isnull=True).order_by('label'),required=False, label=_('Activity'))

    location = forms.CharField(required=False, label=_('Location'))
    location_buffer = forms.IntegerField(required=False, label=_('Location buffer'))
    location_id = forms.IntegerField(required=False)

    thematic = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))
    thematic2 = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))

    mode = forms.MultipleChoiceField(required=False, choices=EMODE, widget=CustomCheckboxSelectMultiple())

    free_search = forms.CharField(required=False, label=_('Free search'))

    
    class Meta:
        model = PageApp_CoopService
   
   
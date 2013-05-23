# -*- coding: utf-8 -*-

from django.utils.translation import ugettext, ugettext_lazy as _
import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from .models import PageApp_CoopExchange

from coop.exchange.models import ETYPE
from coop.exchange.models import EWAY
from coop.exchange.admin import ExchangeForm
from coop_local.models import Exchange
from coop_local.widgets import CustomCheckboxSelectMultiple
from coop.base_models import ActivityNomenclature, TransverseTheme

from extended_choices import Choices



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

    activity = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.all(),required=False, label=_('Activity'))
    activity2 = forms.ModelChoiceField(queryset=ActivityNomenclature.objects.all(),required=False, label=_('Activity'))
    
    location = forms.CharField(required=False, label=_('Location'))
    location_buffer = forms.IntegerField(required=False, label=_('Location buffer'))
    thematic = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))
    thematic2 = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))
    thematic3 = forms.ModelChoiceField(queryset=TransverseTheme.objects.all(), required=False, label=_('Thematic'))
    
    mode = forms.MultipleChoiceField(required=False, choices=EMODE, widget=CustomCheckboxSelectMultiple())
    
    skills = forms.MultipleChoiceField(required=False, choices=ESKILLS, widget=CustomCheckboxSelectMultiple())
    
    free_search = forms.CharField(required=False, label=_('Free search'))
    
    
    class Meta:
        model = PageApp_CoopExchange

        
class PartialExchangeForm(ExchangeForm):
    class Meta:
        model = Exchange
        exclude = ('products', 'sites', )
        
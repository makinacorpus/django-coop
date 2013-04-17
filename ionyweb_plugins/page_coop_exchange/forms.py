# -*- coding: utf-8 -*-

from django.utils.translation import ugettext, ugettext_lazy as _
import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from .models import PageApp_CoopExchange

from coop.exchange.models import ETYPE
from coop.exchange.models import EWAY

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

    type_exchange = forms.MultipleChoiceField(required=False, choices=EWAY, widget=forms.CheckboxSelectMultiple())

    type = forms.MultipleChoiceField(required=False, choices=ETYPE, widget=forms.CheckboxSelectMultiple())

    activity = forms.CharField(required=False, label=_('Activity'))
    location = forms.CharField(required=False, label=_('Location'))
    thematic = forms.CharField(required=False, label=_('Thematic'))
    
    mode = forms.MultipleChoiceField(required=False, choices=EMODE, widget=forms.CheckboxSelectMultiple())
    
    skills = forms.MultipleChoiceField(required=False, choices=ESKILLS, widget=forms.CheckboxSelectMultiple())
    
    free_search = forms.CharField(required=False, label=_('Free search'))
    
    
    class Meta:
        model = PageApp_CoopExchange


class PageApp_CoopExchangeNewForm(ModuloModelForm):

    date_creation = forms.CharField(required=False, label=_('Activity'))
    date_validity = forms.CharField(required=False, label=_('Activity'))
    organization = forms.CharField(required=False, label=_('Activity'))
    organizatiokn_person = forms.CharField(required=False, label=_('Activity'))
    title = forms.CharField(required=False, label=_('Activity'))
    type_exchange = forms.MultipleChoiceField(required=False, choices=EWAY, widget=forms.RadioSelect())
    type = forms.MultipleChoiceField(required=False, choices=ETYPE, widget=forms.RadioSelect())
    mode = forms.MultipleChoiceField(required=False, choices=EMODE, widget=forms.CheckboxSelectMultiple())
    skills = forms.MultipleChoiceField(required=False, choices=ESKILLS, widget=forms.CheckboxSelectMultiple())
    
    date_start = forms.CharField(required=False, label=_('Activity'))
    date_end = forms.CharField(required=False, label=_('Activity'))
    
    location_dep = forms.CharField(required=False, label=_('Activity'))
    location_city = forms.CharField(required=False, label=_('Activity'))
    location_other = forms.CharField(required=False, label=_('Activity'))
    location_zone = forms.CharField(required=False, label=_('Activity'))
    
    description = forms.CharField(required=False, label=_('Activity'))
    thematic = forms.CharField(required=False, label=_('Thematic'))
    activity = forms.CharField(required=False, label=_('Activity'))
    
    key_words = forms.CharField(required=False, label=_('Activity'))
    
    media = forms.CharField(required=False, label=_('Activity'))
        
    
        
    class Meta:
        model = PageApp_CoopExchange        
# -*- coding: utf-8 -*-

import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from django.forms import ModelForm
from .models import PageApp_Members
from django.utils.translation import ugettext, ugettext_lazy as _

class PageApp_MembersForm(ModelForm):

    type = forms.CharField(required=False, label=_('Type'))
    
    activity = forms.CharField(required=False, label=_('Activity'))
    location = forms.CharField(required=False, label=_('Location'))
    location_buffer = forms.CharField(required=False, label=_('Location buffer'))
    thematic = forms.CharField(required=False, label=_('Thematic'))
   
    free_search = forms.CharField(required=False, label=_('Free search'))
    
    class Meta:
        model = PageApp_Members
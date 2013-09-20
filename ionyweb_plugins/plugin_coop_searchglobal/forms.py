# -*- coding: utf-8 -*-
import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from .models import Plugin_CoopSearchGlobal
from django.utils.translation import ugettext, ugettext_lazy as _
from django import forms

class Plugin_CoopSearchGlobalForm(ModuloModelForm):
    
    search_string = forms.CharField(label=_('Search string'), required=False)
    
    class Meta:
        model = Plugin_CoopSearchGlobal
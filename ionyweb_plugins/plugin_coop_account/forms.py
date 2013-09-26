# -*- coding: utf-8 -*-
import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from .models import Plugin_CoopAccount
from django.utils.translation import ugettext, ugettext_lazy as _
from django import forms

class Plugin_CoopAccountForm(ModuloModelForm):
    
    search_string_tag = forms.CharField(label=_('Search string tag'), required=False, widget = forms.HiddenInput())
    
    class Meta:
        model = Plugin_CoopAccount
# -*- coding: utf-8 -*-
import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from .models import Plugin_CoopPromote
from django.utils.translation import ugettext, ugettext_lazy as _
from django import forms

class Plugin_CoopPromoteForm(ModuloModelForm):
    
    dest = forms.EmailField(label=_('Dest'))
    msg = forms.CharField(label=_('Message'), required=False)
    
    class Meta:
        model = Plugin_CoopPromote
# -*- coding: utf-8 -*-

import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from .models import PageApp_CoopAccount
from django.utils.translation import ugettext, ugettext_lazy as _

class PageApp_CoopAccountForm(ModuloModelForm):
    
    class Meta:
        model = PageApp_CoopAccount

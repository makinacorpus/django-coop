# -*- coding: utf-8 -*-
from django.utils.translation import ugettext, ugettext_lazy as _

import floppyforms as forms
from extended_choices import Choices

from ionyweb.forms import ModuloModelForm

from models import PageApp_CoopNewsletter, GuestNewsletter

class PageApp_CoopNewsletterForm(ModuloModelForm):
    
    class Meta:
        model = PageApp_CoopNewsletter


class GuestNewsletterForm(ModuloModelForm):
    class Meta:
        model = GuestNewsletter        
        

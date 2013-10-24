# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.translation import ugettext_lazy as _

from ionyweb.forms import ModuloModelForm, IonywebContentForm

import floppyforms as forms

from models import Plugin_CoopNewsletter, GuestNewsletter



class Plugin_CoopNewsletterForm(ModuloModelForm):

    class Meta:
        model = Plugin_CoopNewsletter


class GuestNewsletterForm(ModuloModelForm):
    class Meta:
        model = GuestNewsletter
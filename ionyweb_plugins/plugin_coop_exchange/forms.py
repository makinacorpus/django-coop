# -*- coding: utf-8 -*-
import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from .models import Plugin_CoopExchange


class Plugin_CoopExchangeForm(ModuloModelForm):

    class Meta:
        model = Plugin_CoopExchange
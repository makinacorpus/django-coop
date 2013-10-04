# -*- coding: utf-8 -*-
import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from .models import Plugin_CoopZoomOn


class Plugin_CoopZoomOnForm(ModuloModelForm):

    class Meta:
        model = Plugin_CoopZoomOn
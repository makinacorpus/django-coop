# -*- coding: utf-8 -*-
import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from .models import Plugin_CoopMembers


class Plugin_CoopMembersForm(ModuloModelForm):

    class Meta:
        model = Plugin_CoopMembers
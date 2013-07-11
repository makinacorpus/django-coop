# -*- coding: utf-8 -*-
import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from .models import Plugin_CoopBlog


class Plugin_CoopBlogForm(ModuloModelForm):

    class Meta:
        model = Plugin_CoopBlog
# -*- coding: utf-8 -*-

from django.utils.translation import ugettext, ugettext_lazy as _
import floppyforms as forms
from ionyweb.forms import ModuloModelForm
from .models import PageApp_CoopSearchGlobal

from coop_local.widgets import CustomCheckboxSelectMultiple, CustomClearableFileInput
from coop.base_models import ActivityNomenclature, TransverseTheme
from extended_choices import Choices

from coop_local.models import LegalStatus, Location, Area

CONTENT_TYPES = Choices (
    ('Exchange',    1,  _(u'Exchange')),
    ('Event',   2,  _(u'Event')),
    ('Organization',   3,  _(u'Organization')),
    ('Project',    4,  _(u'Project')),
    ('Service',      5,  _(u'Service')),
)



class PageApp_CoopSearchGlobalForm(ModuloModelForm):

    class Meta:
        model = PageApp_CoopSearchGlobal
   
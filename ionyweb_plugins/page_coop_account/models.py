# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from extended_choices import Choices

from ionyweb.page.models import AbstractPageApp
from coop_local.models import Organization, ActivityNomenclature, Area, TransverseTheme


class PageApp_CoopAccount(AbstractPageApp):
    
    # Define your fields here

    def __unicode__(self):
        return u'CoopAccount #%d' % (self.pk)

    class Meta:
        verbose_name = _(u"CoopAccount")


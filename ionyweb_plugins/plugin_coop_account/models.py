# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ionyweb.plugin.models import AbstractPlugin


class Plugin_CoopAccount(AbstractPlugin):
    
    # Define your fields here
    account_url = models.CharField(_('Account url'), blank=True, max_length=250)

    def __unicode__(self):
        return u'CoopAccount #%d' % (self.pk)

    class Meta:
        verbose_name = _(u"CoopAccount")
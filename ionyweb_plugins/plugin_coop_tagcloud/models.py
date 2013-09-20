# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ionyweb.plugin.models import AbstractPlugin


class Plugin_CoopTagCloud(AbstractPlugin):
    
    # Define your fields here

    def __unicode__(self):
        return u'CoopTagCloud #%d' % (self.pk)

    class Meta:
        verbose_name = _(u"CoopTagCloud")
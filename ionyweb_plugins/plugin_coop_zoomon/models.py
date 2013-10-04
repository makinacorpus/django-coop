# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ionyweb.plugin.models import AbstractPlugin


class Plugin_CoopZoomOn(AbstractPlugin):

    # Define your fields here
    max_item = models.PositiveIntegerField(u'Nombre d\'items max', default=6)
    filter = models.CharField(u'Filter', default="", max_length=256)

    def __unicode__(self):
        return u'Zoom on #%d' % (self.pk)

    class Meta:
        verbose_name = _(u"Zoom on")
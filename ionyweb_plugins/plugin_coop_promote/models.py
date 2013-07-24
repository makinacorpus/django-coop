# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ionyweb.plugin.models import AbstractPlugin


class Plugin_CoopPromote(AbstractPlugin):
    
    # Define your fields here
    #promote_url = models.CharField(_('Agenda url'), blank=True, max_length=250)
    

    def __unicode__(self):
        return u'CoopPromote #%d' % (self.pk)

    class Meta:
        verbose_name = _(u"CoopPromote")
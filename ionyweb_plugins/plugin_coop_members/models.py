# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ionyweb.plugin.models import AbstractPlugin


class Plugin_CoopMembers(AbstractPlugin):
    
    # Define your fields here
    members_url = models.CharField(_('Members url'), blank=True, max_length=250)
    
    nb_members =  models.IntegerField(_('nb_members'), blank=True, max_length=100)

    def __unicode__(self):
        return u'CoopMembers #%d' % (self.pk)

    class Meta:
        verbose_name = _(u"CoopMembers")
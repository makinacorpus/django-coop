# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ionyweb.plugin.models import AbstractPlugin


class Plugin_CoopExchange(AbstractPlugin):
    
    # Define your fields here
    exchange_url = models.CharField(_('Exchanges url'), blank=True, max_length=250)
    
    nb_exchanges =  models.IntegerField(_('nb_exchanges'), blank=True, max_length=100)

    def __unicode__(self):
        return u'CoopExchanges #%d' % (self.pk)

    class Meta:
        verbose_name = _(u"CoopExchanges")
# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ionyweb.page.models import AbstractPageApp


class PageApp_CoopTerritory(AbstractPageApp):
    
    organizations_url = models.CharField(_('Organizations url'), blank=True, max_length=250)
    exchanges_url = models.CharField(_('Exchanges url'), blank=True, max_length=250)
    agenda_url = models.CharField(_('Agenda url'), blank=True, max_length=250)
    blog_url = models.CharField(_('Blog url'), blank=True, max_length=250)
    
    def __unicode__(self):
        return u'CoopTerritory #%d' % (self.pk)

    class Meta:
        verbose_name = _(u"CoopTerritory")
# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from ionyweb.plugin.models import AbstractPlugin


class Plugin_CoopBlog(AbstractPlugin):
    
    # Define your fields here
    blog_url = models.CharField(_('Agenda url'), blank=True, max_length=250)
    
    nb_news =  models.IntegerField(_('nb_events'), blank=True, max_length=100)

    def __unicode__(self):
        return u'CoopBlog #%d' % (self.pk)

    class Meta:
        verbose_name = _(u"CoopBlog")